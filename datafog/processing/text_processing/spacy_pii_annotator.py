import logging
from typing import Any, Dict, List

from pydantic import BaseModel
from datafog.models.annotator import AnnotationResult

PII_ANNOTATION_LABELS = [
    "CARDINAL",
    "DATE",
    "EVENT",
    "FAC",
    "GPE",
    "LANGUAGE",
    "LAW",
    "LOC",
    "MONEY",
    "NORP",
    "ORDINAL",
    "ORG",
    "PERCENT",
    "PERSON",
    "PRODUCT",
    "QUANTITY",
    "TIME",
    "WORK_OF_ART",
]
MAXIMAL_STRING_SIZE = 1000000


class SpacyPIIAnnotator(BaseModel):
    nlp: Any

    @classmethod
    def create(cls) -> "SpacyPIIAnnotator":
        import spacy

        try:
            nlp = spacy.load("en_core_web_lg")
        except OSError:
            import subprocess
            import sys

            interpreter_location = sys.executable
            subprocess.run(
                [
                    interpreter_location,
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "--no-cache-dir",
                    "https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.7.1/en_core_web_lg-3.7.1-py3-none-any.whl",
                ],
                check=True,
            )
            nlp = spacy.load("en_core_web_lg")
        # Add custom patterns
        ruler = nlp.add_pipe("entity_ruler", after="ner")
        ruler.matcher.validate = True  # Enable validation
        patterns = [
            {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
            {"label": "PHONE_NUMBER",
             "pattern": [{"ORTH": "+", "OP": "?"}, {"SHAPE": "ddd"}, {"ORTH": "-", "OP": "?"}, {"SHAPE": "ddd"},
                         {"ORTH": "-", "OP": "?"}, {"SHAPE"
                                                    "dddd"}]},
        ]
        ruler.add_patterns(patterns)
        return cls(nlp=nlp)

    # def annotate(self, text: str) -> Dict[str, List[str]]:
    #     try:
    #         if not text:
    #             return {label: [] for label in PII_ANNOTATION_LABELS}
    #         if len(text) > MAXIMAL_STRING_SIZE:
    #             text = text[:MAXIMAL_STRING_SIZE]
    #         doc = self.nlp(text)
    #         classified_entities = {label: [] for label in PII_ANNOTATION_LABELS}
    #         for ent in doc.ents:
    #             if ent.label_ in classified_entities:
    #                 classified_entities[ent.label_].append(ent.text)
    #         return classified_entities
    #     except Exception as e:
    #         logging.error(f"Error processing text for PII annotations: {str(e)}")
    #         return {
    #             label: [] for label in PII_ANNOTATION_LABELS
    #         }  # Return empty annotations in case of error

    def annotate(self, text: str) -> List[AnnotationResult]:
        try:
            if not text:
                return []
            if len(text) > MAXIMAL_STRING_SIZE:
                text = text[:MAXIMAL_STRING_SIZE]
            doc = self.nlp(text)
            results = []
            for ent in doc.ents:
                result = AnnotationResult(
                    start=ent.start_char,
                    end=ent.end_char,
                    score=0.8,  # Adjust the score as needed
                    entity_type=ent.label_,
                    recognition_metadata=None,
                )
                results.append(result)
            return results
        except Exception as e:
            logging.error(f"Error processing text for PII annotations: {str(e)}")
            return []  # Return empty list in case of error

        class Config:
            arbitrary_types_allowed = True
