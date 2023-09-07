import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from schemas.user import UserSignInSchema
from services.auth import AuthService
from tests.factories.user import UserFactory
from tests.factories.utils import get_random_email, get_random_str


@pytest.mark.asyncio
async def test__sign_in__success_case(async_db_session: AsyncSession, api_client: AsyncClient) -> None:
    password = get_random_str()
    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(password=password),
    )
    user_data = UserSignInSchema(email=user.email, password=password).model_dump()

    response = await api_client.post("/api/v1/auth/sign-in", json=user_data)
    response_data = response.json()

    user_query_from_db = await async_db_session.execute(select(User).filter_by(email=user.email))
    user_from_db: User = user_query_from_db.scalar_one()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["auth_token"] == user_from_db.auth_token


@pytest.mark.asyncio
async def test__sign_in__invalid_password(async_db_session: AsyncSession, api_client: AsyncClient) -> None:
    user = await UserFactory.create(session=async_db_session)
    user_data = UserSignInSchema(email=user.email, password=get_random_str()).model_dump()

    response = await api_client.post("/api/v1/auth/sign-in", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test__sign_in__user_not_exists(api_client: AsyncClient) -> None:
    user_data = UserSignInSchema(email=get_random_email(), password=get_random_str()).model_dump()

    response = await api_client.post("/api/v1/auth/sign-in", json=user_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
