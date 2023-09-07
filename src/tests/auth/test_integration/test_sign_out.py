import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from tests.factories.user import UserFactory
from tests.utils import get_auth_credentials


@pytest.mark.asyncio
async def test__sign_out__success_case(async_db_session: AsyncSession, api_client: AsyncClient) -> None:
    user = await UserFactory.create(session=async_db_session)
    auth_credentials = get_auth_credentials(auth_token=user.auth_token)

    response = await api_client.post("/api/v1/auth/sign-out", headers=auth_credentials.headers)

    user_query_from_db = await async_db_session.execute(select(User).filter_by(email=user.email))
    user_from_db: User = user_query_from_db.scalar_one()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert user_from_db.auth_token is None


@pytest.mark.asyncio
async def test__sign_out__unauthorized_user(async_db_session: AsyncSession, api_client: AsyncClient) -> None:
    await UserFactory.create(session=async_db_session)

    response = await api_client.post("/api/v1/auth/sign-out")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
