__all__ = ["MissingEnvironmentVariable"]


class MissingEnvironmentVariable(RuntimeError):
    """Exception raised when an environment variable is missing

    These are not necessarily checked on startup, because they may be unused
    during a given test run, and random unrelated crashes would be annoying
    """

    def __init__(self, variable: str):
        super().__init__(f"Missing environment variable: {variable}")
