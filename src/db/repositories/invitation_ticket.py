from db.repositories.base import BaseRedisRepository
from schemas.base import RedisKeySchema
from schemas.ticket import InvitationTicketSchema


class InvitationTicketRepository(BaseRedisRepository):
    schema = InvitationTicketSchema
    key_schema = RedisKeySchema(prefix="invitation_tickets")
