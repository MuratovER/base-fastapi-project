from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.config import settings
from db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/example", status_code=status.HTTP_201_CREATED)
async def example(
    example_service: ExampleService = Depends(),
) -> RegistrationTicketSchema:
    return await example_service.create_link()
