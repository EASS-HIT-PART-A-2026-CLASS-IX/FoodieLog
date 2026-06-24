import hashlib
import json
from dataclasses import dataclass

from fastapi import Query, Request, Response


@dataclass
class Page:
    number: int
    size: int


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> Page:
    return Page(number=page, size=page_size)


def compute_etag(data: list) -> str:
    digest = hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()
    return f'W/"{digest}"'


def maybe_not_modified(request: Request, response: Response, etag: str) -> bool:
    response.headers["ETag"] = etag
    if request.headers.get("if-none-match") == etag:
        return True
    return False
