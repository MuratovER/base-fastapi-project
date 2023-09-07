from fastapi import APIRouter

from api.v1.auth import router as auth_router
from api.v1.quarter import router as quarter_router
from api.v1.review import router as review_router
from api.v1.reviewers import router as reviewer_router
from api.v1.template import router as template_router
from api.v1.user import router as user_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(user_router)
v1_router.include_router(auth_router)
v1_router.include_router(review_router)
v1_router.include_router(template_router)
v1_router.include_router(reviewer_router)
v1_router.include_router(quarter_router)

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
