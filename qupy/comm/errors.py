class CommError(Exception):
    pass

class CommTimeoutError(CommError):
    pass

class CommClientError(CommError):
    pass
