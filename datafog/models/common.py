# models/common.py
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class EntityTypes(str, Enum):
    # Define your entity types here
    PERSON = "Names similar to John Doe, Joe Biden, Donald Trump, Kamala Harris"
    LOCATION = "Full or partial name of a location"
    ORGANIZATION = "Full or partial name of an organization"
    EMAIL = "email address (containing @)"
    PHONE_NUMBER = (
        "phone number (containing numbers and possibly dashes or parentheses)"
    )
    DATE = "date (in any format)"
    NUMBER = "number (in any format)"
    CREDIT_CARD = "credit card number (in any format)"
    UNKNOWN = "Unknown entity type"


class Pattern(BaseModel):
    name: str
    regex: str
    score: float


class PatternRecognizer(BaseModel):
    name: str
    supported_language: str
    patterns: List[Pattern]
    deny_list: Optional[List[str]]
    context: Optional[List[str]]
    supported_entity: str


class AnnotatorMetadata(BaseModel):
    recognizer_name: str
