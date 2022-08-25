__all__ = ["MissingEnvironmentVariable"]


class MissingEnvironmentVariable(RuntimeError):
    """Exception raised when an environment variable is missing"""

    def __init__(self, variable_name):
        super().__init__(f"Missing environment variable: {variable_name}")
