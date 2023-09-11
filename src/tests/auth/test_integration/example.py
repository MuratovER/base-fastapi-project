# import pytest
# from fastapi import status
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
#
#
# @pytest.mark.asyncio
# async def test__ticket_auth__success_case(
#     async_db_session: AsyncSession, api_client: AsyncClient, async_redis_client: AsyncRedis, auth_token: str | None
# ) -> None:
#     example_model = await ExampleFactory(session=async_db_session, auth_token=auth_token)
#     # some logic
#
#     response = await api_client.post(f"/api/v1/example/")
#     response_data = response.json()
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response_data["some_field"] == example_model.some_field
#

