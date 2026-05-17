from fastapi import APIRouter, Depends

from domain.entities.user import User
from drivers.rest.dependencies.security import get_user_from_access_token
from drivers.rest.dependencies.usecases import get_list_user_bets_history_use_case
from drivers.rest.routers.v1.bet.schema import BetItem
from drivers.rest.routers.v1.bets.schema import BetListResponse
from usecases.users.list_user_bets_history import ListUserBetsHistoryUseCase

router = APIRouter(tags=["bets"])


@router.get("/bets", response_model=BetListResponse)
async def list_bets(
    user: User = Depends(get_user_from_access_token),
    list_user_bets_use_case: ListUserBetsHistoryUseCase = Depends(
        get_list_user_bets_history_use_case
    ),
) -> BetListResponse:
    bets = await list_user_bets_use_case(str(user.id))
    return BetListResponse(items=[BetItem.from_entity(bet) for bet in bets])
