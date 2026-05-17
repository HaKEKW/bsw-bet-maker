from typing import Annotated

from fastapi import Depends

from adapters.line_provider.line_provider import BswLineProvider
from config.settings import Settings, get_settings
from ports.api.line_provider_api import LineProviderApi


def get_line_provider_api(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LineProviderApi:
    return BswLineProvider(settings)
