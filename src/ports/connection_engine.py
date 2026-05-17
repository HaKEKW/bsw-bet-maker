from abc import ABC, abstractmethod


class ConnectionEngine(ABC):
    @abstractmethod
    async def close(self) -> None:
        pass
