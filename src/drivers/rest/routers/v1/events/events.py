from fastapi import APIRouter, Depends

from drivers.rest.dependencies.usecases import get_list_events_use_case
from drivers.rest.routers.v1.events.schema import EventItem, EventListResponse
from usecases.events.list_events_use_case import ListEventsUseCase

router = APIRouter(tags=["events"])


@router.get("/events", response_model=EventListResponse)
async def list_events(
    list_events_use_case: ListEventsUseCase = Depends(get_list_events_use_case),
) -> EventListResponse:
    events = await list_events_use_case()
    return EventListResponse(items=[EventItem.from_entity(event) for event in events])
