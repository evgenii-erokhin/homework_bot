class IncorrectStatusCode(Exception):
    pass


class CannotDecodJson(Exception):
    pass


class RequestFailed(Exception):
    pass


class ConnectionFailed(Exception):
    pass


class TelegramErrorMessage(Exception):
    pass
