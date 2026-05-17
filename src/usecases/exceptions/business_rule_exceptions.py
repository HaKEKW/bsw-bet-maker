class BaseBusinessRuleException(Exception):
    pass


class BetDeadlinePassedException(BaseBusinessRuleException):
    def __str__(self) -> str:
        return "Bet deadline has passed for this event"
