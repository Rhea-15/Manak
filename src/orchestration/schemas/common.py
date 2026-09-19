from enum import Enum

from pydantic import BaseModel


class Language(str, Enum):
    en = "en"
    hi = "hi"
    hinglish = "hinglish"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
