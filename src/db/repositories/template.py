import typing
from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import contains_eager, joinedload

from core.enums import ReviewStatusEnum
from db.models import Answer, DepartmentTemplate, Question, Review, Template, User
from db.repositories.base import BaseDatabaseRepository
from schemas.template import CreateTemplate, UpdateTemplateSchema


class TemplateRepository(BaseDatabaseRepository):
    async def get_template_by_id(self, template_id: int) -> Template | None:
        return await self._session.get(Template, template_id)

    async def refresh_template_with_questions(self, template: Template) -> None:
        await self._session.refresh(
            template,
            [
                "questions",
            ],
        )

    async def get_template_by_id_with_question(self, template_id: int) -> Template | None:
        query = select(Template).options(joinedload(Template.questions)).filter(Template.id == template_id)
        query_result = await self._session.execute(query)

        return query_result.scalar()

    async def create_template(self, data_to_create: CreateTemplate) -> Template:
        template = Template()
        template.name = data_to_create.name

        self._session.add(template)
        await self._session.flush()

        return template

    async def update_template_with_questions(self, template: Template, data_to_update: UpdateTemplateSchema) -> None:
        template.name = data_to_update.name
        template.is_archived = template.is_archived

        await self._session.flush()

    async def get_templates(self) -> Sequence[Template]:
        query_result = await self._session.execute(select(Template))

        return query_result.scalars().all()

    async def get_templates_by_department_ids(self, department_ids: Sequence[int]) -> Sequence[Template]:
        query = select(Template).join(DepartmentTemplate).where(DepartmentTemplate.department_id.in_(department_ids))
        query_result = await self._session.execute(query)

        return query_result.scalars().all()

    async def get_review_templates_by_evaluated_user_id_and_statuses_with_questions(
        self,
        evaluated_user_id: int,
        quarter_id: int,
        statuses: typing.Iterable[ReviewStatusEnum],
        is_contains_reviewer: bool = False,
    ) -> Sequence[Template]:
        query = (
            select(Template)
            .join(Question, Question.template_id == Template.id)
            .outerjoin(Answer, Answer.question_id == Question.id)
            .join(
                Review,
                and_(
                    Answer.review_id == Review.id,
                    Review.quarter_id == quarter_id,
                    Review.evaluated_user_id == evaluated_user_id,
                    Review.status.in_(statuses),
                ),
            )
            .execution_options(populate_existing=True)
        )
        if is_contains_reviewer:
            query = query.outerjoin(User, User.id == Answer.reviewer_id).options(
                contains_eager(Template.questions).contains_eager(Question.answers).contains_eager(Answer.reviewer)
            )
        else:
            query = query.options(contains_eager(Template.questions).contains_eager(Question.answers))

        return (await self._session.scalars(query)).unique().all()
