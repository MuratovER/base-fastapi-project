import typing

from sqlalchemy import delete, select

from db.models import Question
from db.repositories.base import BaseDatabaseRepository
from schemas.question import CreateQuestionSchema, UpdateQuestionSchema


class QuestionRepository(BaseDatabaseRepository):
    async def get_questions_by_ids(self, question_ids: list[int]) -> typing.Sequence[Question]:
        query = select(Question).filter(Question.id.in_(question_ids))

        query_result: typing.Sequence[Question] = (await self._session.scalars(query)).all()

        return query_result

    async def get_questions_by_template_id(self, template_id: int) -> typing.Sequence[Question]:
        query = select(Question).filter_by(template_id=template_id)

        query_result: typing.Sequence[Question] = (await self._session.scalars(query)).all()

        return query_result

    async def create_questions(
        self, template_id: int, data_to_create: list[CreateQuestionSchema] | list[UpdateQuestionSchema]
    ) -> list[Question]:
        questions = []

        for data in data_to_create:
            question = Question()
            question.template_id = template_id
            question.text = data.text
            question.description = data.description

            questions.append(question)

        self._session.add_all(questions)

        await self._session.flush()

        return questions

    async def delete_questions(self, question_ids: list[int]) -> None:
        await self._session.execute(delete(Question).where(Question.id.in_(question_ids)))

    async def update_questions(
        self, questions: typing.Sequence[Question], data_to_update: list[UpdateQuestionSchema]
    ) -> None:
        for question in questions:
            data = next((data for data in data_to_update if data.id == question.id), None)
            if data:
                question.text = data.text
                question.description = data.description

        await self._session.flush()
