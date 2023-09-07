"""
Directory for describing app routers.

Each specific router - separate file.

Route example:
from fastapi import APIRouter, Depends
from starlette import status

from db.models import SomeModel
from services.some_service import SomeService
from schemas.some_model import SomeModelSchema

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[SomeModelSchema],
)
async def get_models(some_service: SomeService = Depends()) -> list[SomeModel]:
    return await some_service.get_models()
"""
