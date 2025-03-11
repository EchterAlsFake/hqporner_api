class InvalidCategory(Exception):
    def __init__(self):
        self.msg = "Invalid Category!"


class NoVideosFound(Exception):
    def __init__(self):
        self.msg = "No videos were found!"


class InvalidActress(Exception):
    def __init__(self):
        self.msg = "Invalid Actress!"


class InvalidURL(Exception):
    def __init__(self):
        self.msg = "Invalid URL!"


class NotAvailable(Exception):
    def __init__(self):
        self.msg = "The video is unavailable, because the CDN network which saves the videos has an issue"


class WeirdError(Exception):
    def __init__(self, msg=None):
        if msg is None:
            self.msg = "This is an unexpected error. If you see this, please report it on GitHub, thanks :)"

        else:
            self.msg = msg