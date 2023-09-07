import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.redis import AsyncRedis
from db.repositories.invitation_ticket import InvitationTicketRepository
from schemas.ticket import InvitationTicketSchema
from schemas.user import UserSignUpSchema
from tests.factories.user import UserFactory
from tests.factories.utils import get_random_ticket


@pytest.mark.asyncio
async def test__sign_up__success_case(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis
) -> None:
    key_schema = InvitationTicketRepository.key_schema
    user = await UserFactory.create(session=async_db_session)
    data = UserSignUpSchema.model_validate(user).model_dump()
    await async_db_session.execute(delete(User).where(User.email == data["email"]))
    ticket = get_random_ticket()
    await async_redis_client.set(key_schema.get_key(ticket), InvitationTicketSchema().model_dump_json())
    user_from_db_before_action = await async_db_session.execute(select(User).where(User.email == data["email"]))

    response = await api_client.post(
        f"/api/v1/auth/sign-up?invitation={ticket}",
        json=data,
    )

    user_from_db_after_action = await async_db_session.execute(select(User).where(User.email == data["email"]))
    assert response.status_code == status.HTTP_201_CREATED
    assert user_from_db_before_action.scalar() is None
    assert user_from_db_after_action.scalar() is not None


@pytest.mark.asyncio
async def test__sign_up__user_exist(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis
) -> None:
    user = await UserFactory.create(session=async_db_session)
    data = UserSignUpSchema.model_validate(user).model_dump()
    ticket = get_random_ticket()
    key_schema = InvitationTicketRepository.key_schema
    await async_redis_client.set(key_schema.get_key(ticket), InvitationTicketSchema().model_dump_json())
    user_from_db_before_action = await async_db_session.execute(select(User).where(User.email == data["email"]))

    response = await api_client.post(
        f"/api/v1/auth/sign-up?invitation={ticket}",
        json=data,
    )

    assert user_from_db_before_action.scalar() is not None
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test__sign_up__invalid_ticket(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis
) -> None:
    user = await UserFactory.create(session=async_db_session)
    data = UserSignUpSchema.model_validate(user).model_dump()
    await async_db_session.execute(delete(User).where(User.email == data["email"]))
    ticket = get_random_ticket()
    key_schema = InvitationTicketRepository.key_schema
    await async_redis_client.set(key_schema.get_key(ticket), InvitationTicketSchema().model_dump_json())
    user_from_db_before_action = await async_db_session.execute(select(User).where(User.email == data["email"]))

    response = await api_client.post(
        f"/api/v1/auth/sign-up?invitation={get_random_ticket()}",
        json=data,
    )

    user_from_db_after_action = await async_db_session.execute(select(User).where(User.email == data["email"]))
    assert user_from_db_before_action.scalar() is None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert user_from_db_after_action.scalar() is None


@pytest.mark.asyncio
async def test__sign_up__invalid_request_data(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis
) -> None:
    user = await UserFactory.create(session=async_db_session)
    data = UserSignUpSchema.model_validate(user).model_dump()
    data["username"], data["email"] = None, None
    ticket = get_random_ticket()
    key_schema = InvitationTicketRepository.key_schema
    await async_redis_client.set(key_schema.get_key(ticket), InvitationTicketSchema().model_dump_json())
    user_from_db_before_action = await async_db_session.execute(select(User).where(User.email == data["email"]))

    response = await api_client.post(
        f"/api/v1/auth/sign-up?invitation={ticket}",
        json=data,
    )

    user_from_db_after_action = await async_db_session.execute(select(User).where(User.email == data["email"]))
    assert user_from_db_before_action.scalar() is None
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert user_from_db_after_action.scalar() is None
