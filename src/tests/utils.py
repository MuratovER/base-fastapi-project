import io
import os
import random
from typing import Any, Sequence

import aioboto3
import aiofiles
import botocore.exceptions
from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.enums import FileStorageEnum, ReviewStatusEnum
from db.models import Quarter, Question, Review, Template, User
from db.session import get_engine
from schemas.auth import AuthCredentialsSchema
from schemas.storage import UserAvatarKeySchema
from schemas.template import OutputTemplateSchema
from storages.base import get_updated_path_depending_on_os
from tests.factories.answer import AnswerFactory
from tests.factories.department_template import DepartmentTemplateFactory
from tests.factories.quarter import QuarterFactory
from tests.factories.question import QuestionFactory
from tests.factories.review import ReviewFactory
from tests.factories.template import TemplateFactory
from tests.factories.user import UserFactory
from tests.factories.utils import ReviewersFactoryRandomParams, get_random_auth_token


async def create_database(url: str) -> None:
    url_object = make_url(url)
    database = url_object.database
    url_object = url_object.set(database="postgres")

    engine = get_engine(url=url_object, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE DATABASE "{database}" ENCODING "utf8"'))

    await engine.dispose()


async def database_exists(url: str) -> bool:
    url_object = make_url(url)
    database = url_object.database
    url_object = url_object.set(database="postgres")

    engine = None
    try:
        engine = get_engine(url=url_object, isolation_level="AUTOCOMMIT")
        async with engine.begin() as conn:
            try:
                datname_exists = await conn.scalar(text(f"SELECT 1 FROM pg_database WHERE datname='{database}'"))

            except (ProgrammingError, OperationalError):
                datname_exists = 0

        return bool(datname_exists)

    finally:
        if engine:
            await engine.dispose()


async def drop_database(url: str) -> None:
    url_object = make_url(url)
    database = url_object.database
    url_object = url_object.set(database="postgres")

    engine = get_engine(url=url_object, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        disc_users = f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}' AND pid <> pg_backend_pid();
        """
        await conn.execute(text(disc_users))

        await conn.execute(text(f'DROP DATABASE "{database}"'))

    await engine.dispose()


def get_auth_credentials(
    auth_token: str | None = None,
) -> AuthCredentialsSchema:
    if not auth_token:
        auth_token = get_random_auth_token()
    headers = {"Authorization": f"Bearer {auth_token}"}
    return AuthCredentialsSchema(headers=headers, auth_token=auth_token)


async def get_user_from_db_by_email(session: AsyncSession, email: str) -> User | None:
    user_from_db: User | None = (await session.execute(select(User).where(User.email == email))).scalar()
    return user_from_db


def get_reviewers_random_params(
    start: int = 1,
    finish: int = 3,
    range: int = 40,
) -> ReviewersFactoryRandomParams:
    return ReviewersFactoryRandomParams(start=start, finish=finish, range=range)


async def get_question_from_db_by_template_id(async_db_session: AsyncSession, template_id: int) -> Sequence[Question]:
    query = select(Question).where(Question.template_id == template_id)
    query_result = await async_db_session.execute(query)

    return query_result.scalars().all()


def build_batch_any_questions(template_id: int, min_size: int = 3, max_size: int = 10, size: int | None = None):
    """Create a batch of any questions, randomly sized from min_size to max_size, or equal to size."""
    batch_size = size if size else random.randint(min_size, max_size)

    questions = QuestionFactory.build_batch(
        size=batch_size,
        template_id=template_id,
    )

    return questions


async def create_any_templates_in_db(
    async_db_session: AsyncSession, min_size: int = 3, max_size: int = 10
) -> list[dict[str, Any]]:
    """Create any templates, randomly sized from min_size to max_size."""
    templates = []

    for i in range(random.randint(min_size, max_size)):
        template = await TemplateFactory.create(session=async_db_session)
        data = OutputTemplateSchema.model_validate(template).model_dump()
        templates.append(data)

    return templates


async def create_templates_with_department_relation(
    async_db_session: AsyncSession, department_id: int
) -> list[dict[str, Any]]:
    """
    Create any templates in DB, randomly sized from min_size to max_size,
    with a relationship to a department (department_id).
    """

    templates = await create_any_templates_in_db(async_db_session=async_db_session, min_size=3, max_size=4)

    for template in templates:
        await DepartmentTemplateFactory.create(
            session=async_db_session, department_id=department_id, template_id=template["id"]
        )

    return templates


def get_random_id(min_id: int = 100, max_id: int = 1000) -> int:
    return random.randint(min_id, max_id)


def get_random_count(min_count: int = 3, max_count: int = 10) -> int:
    return random.randint(min_count, max_count)


def is_file_system_storage_type() -> bool:
    return settings().FILE_STORAGE_TYPE == FileStorageEnum.FILESYSTEM


def get_file_path(avatar_key: str) -> str:
    storage_dsn = os.path.join(settings().BASE_DIR, settings().STORAGE_FILE_PATH)
    return os.path.join(storage_dsn, avatar_key)


def get_folder_path(user_id: int) -> str:
    storage_dsn = os.path.join(settings().BASE_DIR, settings().STORAGE_FILE_PATH)

    return os.path.join(os.path.join(storage_dsn, UserAvatarKeySchema().prefix), str(user_id))


async def create_avatar_in_fs_storage(avatar_key: str, data: bytes) -> None:
    file_path = get_file_path(avatar_key=avatar_key)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with aiofiles.open(file_path, "wb") as file:
        await file.write(data)


async def create_avatar_in_s3_storage(s3_session: aioboto3.Session, avatar_key: str, data: bytes) -> None:
    async with s3_session.client("s3", endpoint_url=settings().S3_DSN) as s3_client:
        await s3_client.upload_fileobj(
            Fileobj=io.BytesIO(data),
            Bucket=settings().S3_BUCKET_NAME,
            Key=avatar_key,
            ExtraArgs={"ContentType": "image/png"},
        )


async def get_objects_count_in_fs_storage(user_id: int) -> int:
    folder_path = get_folder_path(user_id=user_id)

    try:
        file_list = os.listdir(folder_path)
    except FileNotFoundError:
        return 0

    return sum(1 for file in file_list if os.path.isfile(os.path.join(folder_path, file)))


async def get_objects_count_in_s3_storage(s3_session: aioboto3.Session) -> int:
    async with s3_session.client("s3", endpoint_url=settings().S3_DSN) as s3_client:
        response = await s3_client.list_objects_v2(Bucket=settings().S3_BUCKET_NAME)
        if "Contents" in response:
            return len(response["Contents"])
        return 0


async def delete_file_from_fs(avatar_key: str) -> None:
    file_path = get_file_path(avatar_key=avatar_key)
    os.remove(file_path)


async def delete_file_from_s3(avatar_key: str, s3_session: aioboto3.Session) -> None:
    async with s3_session.client("s3", endpoint_url=settings().S3_DSN) as s3_client:
        await s3_client.delete_object(Bucket=settings().S3_BUCKET_NAME, Key=avatar_key)


async def is_file_exists_in_fs(avatar_key: str) -> None:
    file_path = get_file_path(avatar_key=avatar_key)

    try:
        async with aiofiles.open(file_path, "rb"):
            pass

    except FileNotFoundError:
        assert False

    await delete_file_from_fs(avatar_key=avatar_key)


async def is_file_exists_in_s3(s3_session: aioboto3.Session, avatar_key: str) -> None:
    avatar_key = get_updated_path_depending_on_os(os.path.join(settings().STORAGE_FILE_PATH, avatar_key))

    try:
        async with s3_session.client("s3", endpoint_url=settings().S3_DSN) as s3_client:
            await s3_client.head_object(Bucket=settings().S3_BUCKET_NAME, Key=avatar_key)
    except botocore.exceptions.ClientError:
        assert False

    await delete_file_from_s3(avatar_key=avatar_key, s3_session=s3_session)


async def get_path_to_avatar_for_s3(avatar_key: str | None) -> str | None:
    if avatar_key is None:
        return None

    storage_dsn = os.path.join(os.path.join(settings().S3_DSN, settings().S3_BUCKET_NAME), settings().STORAGE_FILE_PATH)

    return get_updated_path_depending_on_os(os.path.join(storage_dsn, avatar_key))


async def get_path_to_avatar_for_fs(avatar_key: str | None) -> str | None:
    if avatar_key is None:
        return None

    storage_dsn = os.path.join(settings().BASE_DIR, settings().STORAGE_FILE_PATH)

    return get_updated_path_depending_on_os(os.path.join(storage_dsn, avatar_key))


async def create_answers(async_db_session: AsyncSession, reviews: list[Review], user_id: int) -> None:
    for review in reviews:
        await async_db_session.refresh(review, ["questions"])
        for question in review.questions:
            await AnswerFactory(
                session=async_db_session, review_id=review.id, question_id=question.id, reviewer_id=user_id
            )


async def setup_reviews_response_test_db_data(
    async_db_session: AsyncSession, user_id: int, review_status: ReviewStatusEnum | None = None
) -> list[Template]:
    random_test_params = get_reviewers_random_params()
    templates: list[Template] = await TemplateFactory.create_batch(
        session=async_db_session,
        size=random.randint(random_test_params.start, random_test_params.finish),
    )
    random_reviewer: User = await UserFactory.create(session=async_db_session)
    quarter: Quarter = await QuarterFactory(session=async_db_session, is_active=True)
    reviews: list[Review] = []
    for template in templates:
        await QuestionFactory.create_batch(
            session=async_db_session,
            size=random.randint(random_test_params.start, random_test_params.finish),
            template_id=template.id,
        )
        review = await ReviewFactory(
            session=async_db_session,
            reviewer_id=random_reviewer.id,
            template_id=template.id,
            initiated_by_id=user_id,
            evaluated_user_id=user_id,
            quarter_id=quarter.id,
        )
        if review_status:
            review.status = review_status
        reviews.append(review)

    await create_answers(async_db_session=async_db_session, reviews=reviews, user_id=user_id)

    return templates
