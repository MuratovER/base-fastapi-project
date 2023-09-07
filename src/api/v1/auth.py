from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.config import settings
from core.enums import UserRoleEnum
from db.models import User
from schemas.ticket import RegistrationTicketSchema
from schemas.token import TokenSchema
from schemas.user import UserSignInSchema, UserSignUpSchema
from services.auth import AuthService, get_current_active_user, oauth_client

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/invitation", status_code=status.HTTP_201_CREATED)
async def invitation(
    current_user: Annotated[User, Security(get_current_active_user, scopes=[UserRoleEnum.ADMIN])],
    auth_service: AuthService = Depends(),
) -> RegistrationTicketSchema:
    return await auth_service.create_link()


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def sign_up(
    invitation: str,
    user_data: UserSignUpSchema,
    auth_service: AuthService = Depends(),
) -> TokenSchema:
    return await auth_service.sign_up(registration_ticket=invitation, user_data=user_data)


@router.post("/sign-in", status_code=status.HTTP_200_OK)
async def sign_in(
    user_data: UserSignInSchema,
    auth_service: AuthService = Depends(),
) -> TokenSchema:
    return await auth_service.sign_in(user_data=user_data)


@router.post("/sign-out", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out(
    current_user: Annotated[User, Security(get_current_active_user)],
    auth_service: AuthService = Depends(),
) -> None:
    await auth_service.sign_out(user=current_user)


@router.get("/sign-in-via-google")
async def sign_in_via_google(request: Request) -> RedirectResponse:
    redirect_uri = settings().OAUTH_AUTH_REDIRECT_URL
    return await oauth_client.google.authorize_redirect(request, redirect_uri)


@router.get("/auth-via-google")
async def auth_via_google(request: Request, auth_service: AuthService = Depends()) -> RedirectResponse:
    url = await auth_service.create_user_with_redirect_url(request=request)
    return RedirectResponse(url=url)


@router.post("/token-by-ticket", status_code=status.HTTP_200_OK)
async def get_token_by_ticket(ticket_uuid: str, auth_service: AuthService = Depends()) -> TokenSchema:
    return await auth_service.get_token_by_ticket(ticket=ticket_uuid)
