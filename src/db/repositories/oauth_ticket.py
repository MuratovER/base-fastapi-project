from db.repositories.base import BaseRedisRepository
from schemas.base import RedisKeySchema
from schemas.ticket import OauthTicketSchema


class OauthTicketRepository(BaseRedisRepository):
    schema = OauthTicketSchema
    key_schema = RedisKeySchema(prefix="oauth_tickets")
