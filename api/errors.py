class ApiException(Exception):
    def __init__(self, error, status, level="info", extra=None):
        self.status = status
        if extra is None:
            self.extra = {}
        self.level = level
        self.error = error
