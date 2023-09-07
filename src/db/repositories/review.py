import typing

from sqlalchemy import and_, func, select
from sqlalchemy.orm import contains_eager, joinedload

from core.enums import ReviewStatusEnum
from db.models import Answer, Question, Review, User
from db.repositories.base import BaseDatabaseRepository


class ReviewRepository(BaseDatabaseRepository):
    async def get_review_by_id_and_reviewer_id(self, review_id: int, reviewer_id: int) -> Review | None:
        query = select(Review).options(joinedload(Review.answers)).filter_by(id=review_id, reviewer_id=reviewer_id)

        query_result = await self._session.execute(query)

        return query_result.unique().scalar_one_or_none()

    async def create_review(
        self,
        reviewers: typing.Sequence[User],
        template_id: int,
        evaluated_user_id: int,
        initiated_by_id: int,
        quarter_id: int,
    ) -> list[Review]:
        new_reviews = []

        for reviewer in reviewers:
            new_review = Review()

            new_review.reviewer_id = reviewer.id
            new_review.template_id = template_id
            new_review.evaluated_user_id = evaluated_user_id
            new_review.initiated_by_id = initiated_by_id
            new_review.quarter_id = quarter_id

            new_reviews.append(new_review)

        self._session.add_all(new_reviews)
        await self._session.flush()

        return new_reviews

    async def update_review_status(self, review_instance: Review, status: ReviewStatusEnum) -> None:
        review_instance.status = status

        await self._session.flush()

    async def get_reviews_by_reviewer_id_and_statuses(
        self, statuses: typing.Iterable[ReviewStatusEnum], reviewer_id: int
    ) -> typing.Sequence[Review]:
        query = (
            select(Review)
            .filter_by(reviewer_id=reviewer_id)
            .where(Review.status.in_(statuses))
            .options(joinedload(Review.evaluated_user))
        )
        return (await self._session.scalars(query)).unique().all()

    async def get_completed_reviews_count_by_evaluated_user_id(
        self, evaluated_user_id: int, quarter_id: int
    ) -> int | None:
        query = select(func.count(Review.id)).filter_by(
            evaluated_user_id=evaluated_user_id, quarter_id=quarter_id, status=ReviewStatusEnum.COMPLETED
        )
        return await self._session.scalar(query)

    async def get_all_reviews_count_by_evaluated_user_id(self, evaluated_user_id: int, quarter_id: int) -> int | None:
        query = select(func.count(Review.id)).filter_by(evaluated_user_id=evaluated_user_id, quarter_id=quarter_id)
        return await self._session.scalar(query)

    async def get_reviews_by_reviewer_id_and_quarter_id_without_pending(
        self, reviewer_id: int, quarter_id: int
    ) -> typing.Sequence[Review]:
        query = (
            select(Review)
            .options(joinedload(Review.answers))
            .filter_by(reviewer_id=reviewer_id, quarter_id=quarter_id)
            .where(Review.status.in_([ReviewStatusEnum.DRAFT, ReviewStatusEnum.COMPLETED]))
        )

        return (await self._session.scalars(query)).unique().all()

    async def get_review_by_review_id_and_reviewer_id(self, review_id: int, reviewer_id: int) -> Review | None:
        query = (
            select(Review)
            .options(joinedload(Review.quarter))
            .options(joinedload(Review.evaluated_user))
            .filter_by(id=review_id, reviewer_id=reviewer_id)
            .join(Question, Question.template_id == Review.template_id)
            .outerjoin(Answer, and_(Answer.question_id == Question.id, Answer.review_id == Review.id))
            .options(contains_eager(Review.questions).contains_eager(Question.answers))
        )
        return await self._session.scalar(query)
