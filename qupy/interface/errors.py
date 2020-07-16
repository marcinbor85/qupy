class InterfaceError(Exception):
    pass

class InterfaceIOError(InterfaceError):
    pass

class InterfaceTimeoutError(InterfaceError):
    pass
