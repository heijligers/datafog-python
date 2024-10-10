"""
Common models for DataFog PII detection and annotation.

Defines entity types, patterns, and metadata structures used across the library.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from enum import Enum


class EntityTypes(str, Enum):
    """Entity types recognized by spaCy."""
    PERSON = "PERSON"
    NORP = "NORP"
    FAC = "FAC"
    ORG = "ORG"
    GPE = "GPE"
    LOC = "LOC"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    WORK_OF_ART = "WORK_OF_ART"
    LAW = "LAW"
    LANGUAGE = "LANGUAGE"
    DATE = "DATE"
    TIME = "TIME"
    PERCENT = "PERCENT"
    MONEY = "MONEY"
    QUANTITY = "QUANTITY"
    ORDINAL = "ORDINAL"
    CARDINAL = "CARDINAL"
    EMAIL = "EMAIL"
    PHONE_NUMBER = "PHONE_NUMBER"



class Pattern(BaseModel):
    """Regex pattern for entity recognition."""

    name: str
    regex: str
    score: float


class PatternRecognizer(BaseModel):
    """Configuration for a pattern-based entity recognizer."""

    name: str
    supported_language: str
    patterns: List[Pattern]
    deny_list: Optional[List[str]]
    context: Optional[List[str]]
    supported_entity: str


class AnnotatorMetadata(BaseModel):
    """Metadata for annotation results."""

    recognizer_name: Optional[str] = None
