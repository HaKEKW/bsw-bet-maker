from pydantic import BaseModel

from drivers.rest.routers.v1.bet.schema import BetItem


class BetListResponse(BaseModel):
    items: list[BetItem]
