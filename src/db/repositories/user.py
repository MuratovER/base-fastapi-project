import typing
from typing import Sequence

from sqlalchemy import and_, select

from core.enums import ReviewStatusEnum
from db.models import Review, User
from db.repositories.base import BaseDatabaseRepository
from schemas.user import UserSignUpSchema, UserUpdateExtendedSchema, UserUpdateSchema


class UserRepository(BaseDatabaseRepository):
    """Class contains methods to fetch data from db."""

    async def get_active_user_by_token(self, auth_token: str) -> User | None:
        query = select(User).filter_by(auth_token=auth_token, is_active=True)
        query_result = await self._session.execute(query)
        return query_result.scalar_one_or_none()

    async def get_active_user_by_email(self, email: str) -> User | None:
        query = select(User).filter_by(email=email, is_active=True)
        query_result = await self._session.execute(query)
        return query_result.scalar_one_or_none()

    async def get_active_users_by_ids(self, user_ids: list[int]) -> Sequence[User]:
        query = select(User).filter(User.id.in_(user_ids)).filter_by(is_active=True)

        query_result: Sequence[User] = (await self._session.scalars(query)).all()

        return query_result

    async def get_all_users(self) -> Sequence[User]:
        query = select(User)
        query_result: Sequence[User] = (await self._session.scalars(query)).all()
        return query_result

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).filter_by(id=user_id)
        query_result = await self._session.execute(query)
        return query_result.scalar_one_or_none()

    async def update_user(self, user: User, user_data: UserUpdateSchema | UserUpdateExtendedSchema) -> None:
        user.username = user_data.username
        user.email = user_data.email
        user.first_name = user.first_name
        user.last_name = user_data.last_name
        user.father_name = user_data.father_name
        if isinstance(user_data, UserUpdateExtendedSchema):
            user.role = user_data.role
            user.is_active = user_data.is_active

        await self._session.flush()

    async def update_user_token(self, user: User, auth_token: str | None) -> None:
        user.auth_token = auth_token

        await self._session.flush()

    async def create_user(self, data_to_create: UserSignUpSchema, auth_token: str | None = None) -> User:
        user = User(**data_to_create.model_dump())
        user.auth_token = auth_token
        self._session.add(user)
        await self._session.flush()

        return user

    async def get_active_users(self, exclude_user_id: int | None = None) -> Sequence[User]:
        if exclude_user_id:
            query = select(User).filter_by(is_active=True).where(User.id != exclude_user_id)
        else:
            query = select(User).filter_by(is_active=True)

        return (await self._session.scalars(query)).all()

    async def get_users_by_mentor_id(self, mentor_id: int) -> Sequence[User]:
        query = select(User).filter_by(mentored_by_id=mentor_id)
        return (await self._session.scalars(query)).all()

    async def get_user_ids_by_mentor_id(self, mentor_id: int) -> Sequence[int]:
        query = select(User.id).filter_by(mentored_by_id=mentor_id)
        return (await self._session.scalars(query)).all()

    async def get_users_with_not_completed_review_by_evaluated_user_id(
        self, evaluated_user_id: int, quarter_id: int
    ) -> typing.Sequence[User]:
        query = (
            select(User)
            .join(
                Review,
                and_(
                    Review.reviewer_id == User.id, Review.status.in_([ReviewStatusEnum.DRAFT, ReviewStatusEnum.PENDING])
                ),
            )
            .filter_by(evaluated_user_id=evaluated_user_id, quarter_id=quarter_id)
        )
        return (await self._session.scalars(query)).unique().all()
