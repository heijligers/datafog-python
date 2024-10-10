"""
Text processing service for PII annotation.

Provides synchronous and asynchronous methods for annotating text with personally identifiable information (PII) using SpaCy. Supports chunking long texts and batch processing.
"""

import asyncio
from typing import Dict, List

from datafog.processing.text_processing.spacy_pii_annotator import SpacyPIIAnnotator
from datafog.models.annotator import AnnotationResult

class TextService:
    """
    Manages text annotation operations.

    Handles text chunking, PII annotation, and result combination for both single texts and batches. Offers both synchronous and asynchronous interfaces.
    """

    def __init__(self, text_chunk_length: int = 1000):
        self.annotator = SpacyPIIAnnotator.create()
        self.text_chunk_length = text_chunk_length

    def _chunk_text(self, text: str) -> List[str]:
        """Split the text into chunks of specified length."""
        return [
            text[i : i + self.text_chunk_length]
            for i in range(0, len(text), self.text_chunk_length)
        ]

    def _combine_annotations(self, annotations_list: List[List[AnnotationResult]]) -> List[AnnotationResult]:
        """Combine lists of AnnotationResult from multiple chunks."""
        combined_annotations = []
        for annotation in annotations_list:
            combined_annotations.extend(annotation)
        return combined_annotations

    def annotate_text_sync(self, text: str) -> List[AnnotationResult]:
        """Synchronously annotate a text string."""
        if not text:
            return []
        #print(f"Starting on {text.split()[0]}")
        chunks = self._chunk_text(text)
        annotations_list = []
        for chunk in chunks:
            res = self.annotator.annotate(chunk)
            annotations_list.append(res)
        combined_annotations = self._combine_annotations(annotations_list)
        #print(f"Done processing {text.split()[0]}")
        return combined_annotations

    def batch_annotate_text_sync(self, texts: List[str]) -> List[List[AnnotationResult]]:
        """Synchronously annotate a list of text input."""
        results = [self.annotate_text_sync(text) for text in texts]
        return results

    async def annotate_text_async(self, text: str) -> Dict:
        """Asynchronously annotate a text string."""
        if not text:
            return {}
        chunks = self._chunk_text(text)
        tasks = [asyncio.to_thread(self.annotator.annotate, chunk) for chunk in chunks]
        annotations = await asyncio.gather(*tasks)
        return self._combine_annotations(annotations)

    async def batch_annotate_text_async(self, texts: List[str]) -> Dict[str, Dict]:
        """Asynchronously annotate a list of text input."""
        tasks = [self.annotate_text_async(txt) for txt in texts]
        results = await asyncio.gather(*tasks)
        return dict(zip(texts, results, strict=True))
