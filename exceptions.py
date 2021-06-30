class Exit(Exception):
    """Exception to allow a clean exit from any point in execution
    """
    DATABASE_ERROR = 1
    DATABASE_IS_LOCKED = 2
    DATABASE_UNDEFINED_TABLE = 3
    DATABASE_NOT_FOUND = 4

    OS_NOT_SUPPORTED = 5
    BROWSER_NOT_IMPLEMENTED = 6
    BROWSER_NOT_FOUND = 7
    FILE_NOT_FOUND = 8
    INVALID_HOOK_URL = 9

    NOT_HANDLED = 101
    KEYBOARD_INTERRUPT = 102

    def __init__(self, exitcode):
        self.exitcode = exitcode
