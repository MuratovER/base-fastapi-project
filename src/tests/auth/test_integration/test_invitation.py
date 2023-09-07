import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.redis import AsyncRedis
from db.repositories.invitation_ticket import InvitationTicketRepository
from tests.factories.user import AdminUserFactory, EmployerUserFactory
from tests.utils import get_auth_credentials


@pytest.mark.asyncio
async def test__invitation__valid_scope(
    async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis
) -> None:
    user = await AdminUserFactory.create(session=async_db_session)
    auth_credentials = get_auth_credentials(auth_token=user.auth_token)
    key_schema = InvitationTicketRepository.key_schema

    response = await api_client.post(
        "/api/v1/auth/invitation",
        headers=auth_credentials.headers,
    )

    response_data = response.json()
    ticket = response_data["registration_ticket"]
    ticket_from_db = await async_redis_client.get(key_schema.get_key(ticket))

    assert response.status_code == status.HTTP_201_CREATED
    assert ticket_from_db


@pytest.mark.asyncio
async def test__invitation__user_not_authorized(api_client: AsyncClient) -> None:
    response = await api_client.post(
        "/api/v1/auth/invitation",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test__invitation__not_permitted(async_db_session: AsyncSession, api_client: AsyncClient) -> None:
    user = await EmployerUserFactory.create(session=async_db_session)
    auth_credentials = get_auth_credentials(auth_token=user.auth_token)

    response = await api_client.post(
        "/api/v1/auth/invitation",
        headers=auth_credentials.headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
