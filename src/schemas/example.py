from schemas.base import BaseOrmSchema


class ExampleSchema(BaseOrmSchema):
    id: int
    text: str
