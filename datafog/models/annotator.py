# models/annotator.py
from typing import List, Optional

from pydantic import BaseModel, field_validator

from .common import AnnotatorMetadata, EntityTypes, PatternRecognizer


class AnnotatorRequest(BaseModel):
    text: str
    language: str
    correlation_id: Optional[str]
    score_threshold: Optional[float]
    entities: Optional[List[EntityTypes]]
    return_decision_process: Optional[bool]
    ad_hoc_recognizers: Optional[List[PatternRecognizer]]
    context: Optional[List[str]]


class AnnotationResult(BaseModel):
    start: int
    end: int
    score: float
    entity_type: str
    recognition_metadata: Optional[AnnotatorMetadata]

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v):
        if v not in EntityTypes.__members__:
            return "UNKNOWN"
        return v


class AnalysisExplanation(BaseModel):
    recognizer: str
    pattern_name: Optional[str]
    pattern: Optional[str]
    original_score: float
    score: float
    textual_explanation: Optional[str]
    score_context_improvement: float
    supportive_context_word: str
    validation_result: Optional[float]


class AnnotationResultWithAnaysisExplanation(AnnotationResult):
    analysis_explanation: Optional[AnalysisExplanation]
