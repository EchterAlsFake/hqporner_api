class InvalidActress(Exception):
    def __init__(self):
        self.message = "Invalid Actress!"


class NotAvailable(Exception):
    def __init__(self):
        self.message = "The video is unavailable, because the CDN network which saves the videos has an issue"


class NotFound(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NetworkError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class BotDetection(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ProxyError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UnknownNetworkError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class DownloadFailed(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message