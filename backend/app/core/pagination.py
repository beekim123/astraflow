from typing import Any


def page_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size


def page_payload(items: list[Any], total: int, page: int, page_size: int) -> dict[str, Any]:
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
