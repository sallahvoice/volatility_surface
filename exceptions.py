class QueryError(Exception):
    def __init__(self, message: str, value: str) -> None:
        super().__init__(message)
        self.message = message
        self.value = value

    def __str__(self) -> str:
        return f"{self.message}, (value: {self.value})"
