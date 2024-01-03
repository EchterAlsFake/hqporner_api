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
