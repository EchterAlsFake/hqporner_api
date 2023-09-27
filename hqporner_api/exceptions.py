class QualityNotSupported(Exception):
    def __int__(self):
        self.msg = "Quality not supported by video"


class ActressNotFound(Exception):
    def __init__(self, name):
        self.msg = f"Actress: {name} wasn't found on hqporner.com Note: If a name is separated with space, use a dash as connector"


class NoActressFound(Exception):
    def __int__(self):
        self.msg = "Couldn't extract actress."
