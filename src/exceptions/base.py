from http import HTTPStatus


class AppException(Exception):
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)
