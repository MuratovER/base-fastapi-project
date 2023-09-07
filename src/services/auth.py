import urllib.parse
from uuid import uuid4

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from loguru import logger
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from core.config import settings
from core.enums import UserRoleEnum
from core.exceptions import (
    not_enough_permission_exception,
    not_valid_credentials_exception,
    oauth_bad_response,
    oauth_data_missed_exception,
    oauth_ticket_not_found_exception,
    ticket_not_found_exception,
    user_already_exists_exception,
    user_not_authorized_exception,
    user_not_found_exception,
)
from db.models import User
from db.repositories.invitation_ticket import InvitationTicketRepository
from db.repositories.oauth_ticket import OauthTicketRepository
from db.repositories.user import UserRepository
from db.session import get_session
from schemas.ticket import (
    InvitationTicketSchema,
    OauthTicketSchema,
    RegistrationTicketSchema,
)
from schemas.token import TokenSchema
from schemas.user import UserSignInSchema, UserSignUpSchema

oauth2_scheme = HTTPBearer(auto_error=False)
oauth_client = OAuth()
config = settings()

oauth_client.register(
    name="google",
    server_metadata_url=config.GOOGLE_OAUTH_CONF_URL,
    client_kwargs={
        "scope": config.OAUTH_SCOPE,
        "prompt": config.GOOGLE_OAUTH_PROMPT,
    },
    client_id=config.OAUTH_CLIENT_ID,
    client_secret=config.OAUTH_CLIENT_SECRET_KEY,
)


class AuthService:
    """Class contains methods to validate auth processes."""

    @classmethod
    def verify_password(cls, plain_password: str, hash_password: str) -> bool:
        return bcrypt.verify(plain_password, hash_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def create_token(cls) -> str:
        return str(uuid4())

    @classmethod
    def create_temp_password(cls) -> str:
        return str(uuid4())

    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        ticket_repository: InvitationTicketRepository = Depends(InvitationTicketRepository),
        oauth_repository: OauthTicketRepository = Depends(OauthTicketRepository),
        session: AsyncSession = Depends(get_session),
    ):
        self.user_repository = user_repository
        self.ticket_repository = ticket_repository
        self.oauth_repository = oauth_repository
        self._session = session

    async def create_link(self, expiration_time: int = 3600) -> RegistrationTicketSchema:
        """Create a link for user registration."""
        ticket_model = InvitationTicketSchema()

        ticket_uuid = await self.ticket_repository.set(
            model=ticket_model,
            expiration_seconds=expiration_time,
        )

        return RegistrationTicketSchema(registration_ticket=ticket_uuid)

    async def sign_up(self, registration_ticket: str, user_data: UserSignUpSchema) -> TokenSchema:
        """
        Sign up user.

        Checks for unique email, hash password, creates user in db token.
        """
        ticket = await self.ticket_repository.get(uuid=registration_ticket)
        user = await self.user_repository.get_active_user_by_email(email=user_data.email)

        if not ticket:
            raise ticket_not_found_exception
        if user:
            raise user_already_exists_exception

        user_data.password = self.hash_password(password=user_data.password)

        auth_token = self.create_token()
        await self.user_repository.create_user(data_to_create=user_data, auth_token=auth_token)
        await self.ticket_repository.delete(uuid=registration_ticket)

        await self._session.commit()
        return TokenSchema(auth_token=auth_token)

    async def sign_in(self, user_data: UserSignInSchema) -> TokenSchema:
        """
        Sign in user.

        Validate input user email and password and create auth token.
        If user not found or password is incorrect - raise NotFoundException.
        """
        user = await self.user_repository.get_active_user_by_email(email=user_data.email)

        if not user:
            raise user_not_found_exception
        elif not self.verify_password(user_data.password, user.password):
            raise not_valid_credentials_exception

        auth_token = await self._get_or_update_auth_token(user=user)

        return TokenSchema(auth_token=auth_token)

    async def sign_out(self, user: User) -> None:
        await self.user_repository.update_user_token(user=user, auth_token=None)

    async def create_user_with_redirect_url(self, request: Request) -> str:
        try:
            token = await oauth_client.google.authorize_access_token(request)
        except OAuthError as error:
            logger.exception(error)
            oauth_bad_response.detail = error
            raise oauth_bad_response

        userinfo = token.pop("userinfo")
        if not userinfo:
            logger.exception(f"{oauth_data_missed_exception.detail}; token: {token}")
            raise oauth_data_missed_exception

        email = token.get("email", None)
        first_name = token.get("name", None)
        if not email or not first_name:
            logger.exception(f"{oauth_data_missed_exception.detail}; token: {token}")
            raise oauth_data_missed_exception

        user = await self.user_repository.get_active_user_by_email(email=email)

        if not user:
            user_data = UserSignUpSchema(
                username=first_name,
                first_name=first_name,
                email=email,
                password=self.create_temp_password(),
                role=UserRoleEnum.EMPLOYER,
            )
            user = await self.user_repository.create_user(data_to_create=user_data)

        ticket_uuid = self.oauth_repository.set(InvitationTicketSchema(user_id=user.id), expiration_seconds=15)

        params = {"ticket": ticket_uuid}

        url = config.OAUTH_REDIRECT_AFTER_SIGN_IN_URL
        url += ("&" if urllib.parse.urlparse(url).query else "?") + urllib.parse.urlencode(params)

        return url

    async def get_token_by_ticket(self, ticket: str) -> TokenSchema:
        oauth_ticket: OauthTicketSchema | None = await self.oauth_repository.get(uuid=ticket)  # type: ignore

        if not oauth_ticket:
            raise oauth_ticket_not_found_exception

        user = await self.user_repository.get_user_by_id(user_id=oauth_ticket.user_id)

        if not user:
            raise user_not_authorized_exception

        await self.oauth_repository.delete(uuid=ticket)

        auth_token = await self._get_or_update_auth_token(user=user)

        return TokenSchema(auth_token=auth_token)

    async def _get_or_update_auth_token(self, user: User) -> str:
        if user.auth_token:
            auth_token = user.auth_token
        else:
            auth_token = self.create_token()
            await self.user_repository.update_user_token(user=user, auth_token=auth_token)
            await self._session.commit()

        return auth_token


async def get_current_active_user(
    security_scopes: SecurityScopes,
    auth_token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(),
) -> User:
    """Returns User by auth_token and scopes or raise HTTPException"""
    if not auth_token:
        raise user_not_authorized_exception

    user = await user_repository.get_active_user_by_token(auth_token=auth_token.credentials.split(" ")[-1])

    if not user:
        raise user_not_authorized_exception
    elif security_scopes.scopes and user.role not in security_scopes.scopes:
        raise not_enough_permission_exception

    return user
