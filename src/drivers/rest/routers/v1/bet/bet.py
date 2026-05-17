from fastapi import APIRouter, Depends

from domain.entities.user import User
from drivers.rest.dependencies.security import get_user_from_access_token
from drivers.rest.dependencies.usecases import get_save_bet_use_case
from drivers.rest.routers.v1.bet.schema import BetInput, BetItem
from usecases.bets.save_bet_use_case import SaveBetUseCase

router = APIRouter(tags=["bets"])


@router.post("/bet", response_model=BetItem)
async def create_bet(
    bet_input: BetInput,
    user: User = Depends(get_user_from_access_token),
    save_bet_use_case: SaveBetUseCase = Depends(get_save_bet_use_case),
) -> BetItem:
    bet = await save_bet_use_case(bet_input.to_entity(str(user.id)))
    return BetItem.from_entity(bet)
