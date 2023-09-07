import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    oauth_ticket_not_found_exception,
    user_not_authorized_exception,
)
from db.redis import AsyncRedis
from db.repositories.oauth_ticket import OauthTicketRepository
from schemas.ticket import OauthTicketSchema
from tests.factories.user import UserFactory
from tests.factories.utils import get_random_auth_token, get_random_ticket
from tests.utils import get_random_id


@pytest.mark.asyncio
@pytest.mark.parametrize("auth_token", (get_random_auth_token(), None))
async def test__ticket_auth__success_case(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis, auth_token: str | None
) -> None:
    user = await UserFactory(session=async_db_session, auth_token=auth_token)
    ticket = get_random_ticket()
    redis_ticket = OauthTicketRepository.key_schema.get_key(ticket)
    await async_redis_client.set(name=redis_ticket, value=OauthTicketSchema(user_id=user.id).model_dump_json())
    await async_redis_client.get(redis_ticket)

    response = await api_client.post(f"/api/v1/auth/token-by-ticket?ticket_uuid={ticket}")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["auth_token"] == user.auth_token


@pytest.mark.asyncio
async def test__ticket_auth__invalid_ticket(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis
) -> None:
    user = await UserFactory(session=async_db_session)
    redis_ticket = OauthTicketRepository.key_schema.get_key(get_random_ticket())
    await async_redis_client.set(name=redis_ticket, value=OauthTicketSchema(user_id=user.id).model_dump_json())

    response = await api_client.post(f"/api/v1/auth/token-by-ticket?ticket_uuid={get_random_ticket()}")
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data["detail"] == oauth_ticket_not_found_exception.detail


@pytest.mark.asyncio
async def test__ticket_auth__user_doesnt_exist(api_client: AsyncClient, async_redis_client: AsyncRedis) -> None:
    ticket = get_random_ticket()
    redis_ticket = OauthTicketRepository.key_schema.get_key(ticket)
    await async_redis_client.set(name=redis_ticket, value=OauthTicketSchema(user_id=get_random_id()).model_dump_json())

    response = await api_client.post(f"/api/v1/auth/token-by-ticket?ticket_uuid={ticket}")
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data["detail"] == user_not_authorized_exception.detail
