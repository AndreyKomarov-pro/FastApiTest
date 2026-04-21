from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    size: int

    @classmethod
    def build(cls, items: list[T], page: int, size: int) -> "PageResponse[T]":
        return cls(
            items=items,
            page=page,
            size=size,
        )
