from schemas.base import BaseOrmSchema
from schemas.user import GetSharedReviewOutputUserSchema


class OutputAnswerSchema(BaseOrmSchema):
    id: int
    text: str


class InputAnswerSchema(BaseOrmSchema):
    text: str
    question_id: int


class InputAnswersSchema(BaseOrmSchema):
    answers: list[InputAnswerSchema]


class GetSharedReviewOutputAnswerSchema(BaseOrmSchema):
    id: int
    text: str
    reviewer: GetSharedReviewOutputUserSchema


class GetReviewQuestionsOutputAnswerSchema(BaseOrmSchema):
    id: int
    text: str


class GetMyReviewsOutputAnswerSchema(BaseOrmSchema):
    id: int
    text: str
