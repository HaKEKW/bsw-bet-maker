class MessageValidationException(Exception):
    def __str__(self) -> str:
        return "Invalid message payload"
