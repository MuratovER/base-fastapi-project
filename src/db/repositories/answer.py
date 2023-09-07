import typing

from sqlalchemy import select

from db.models import Answer
from db.repositories.base import BaseDatabaseRepository
from schemas.answer import InputAnswerSchema


class AnswerRepository(BaseDatabaseRepository):
    async def get_answers_by_review_id(self, review_id: int) -> typing.Sequence[Answer]:
        return (await self._session.scalars(select(Answer).filter_by(review_id=review_id))).all()

    async def add_or_update_answers(
        self, review_id: int, reviewer_id: int, answers: list[InputAnswerSchema]
    ) -> list[Answer]:
        new_answers = []
        existing_answers = await self._get_answers_by_review_id_and_questions_id(
            review_id=review_id, question_ids=[answer.question_id for answer in answers]
        )

        for existing_answer, answer_to_update in zip(existing_answers, answers):
            existing_answer.text = answer_to_update.text
            answers.remove(answer_to_update)
            new_answers.append(existing_answer)

        for answer in answers:
            new_answer = Answer(**answer.model_dump())
            new_answer.review_id = review_id
            new_answer.reviewer_id = reviewer_id
            new_answers.append(new_answer)

        self._session.add_all(new_answers)
        await self._session.flush()

        return new_answers

    async def _get_answers_by_review_id_and_questions_id(
        self, review_id: int, question_ids: typing.Iterable[int]
    ) -> typing.Sequence[Answer]:
        query = select(Answer).filter_by(review_id=review_id).filter(Answer.question_id.in_(question_ids))
        return (await self._session.scalars(query)).all()
