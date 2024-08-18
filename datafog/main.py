"""
Main module for DataFog.

This module contains the core classes for DataFog:
- DataFog: Main class for running OCR and text processing pipelines.
- TextPIIAnnotator: Class for annotating PII in text.

These classes provide high-level interfaces for image and text processing,
including OCR, PII detection, and annotation.
"""

import json
import logging
from typing import List

from .config import OperationType
from .processing.text_processing.spacy_pii_annotator import SpacyPIIAnnotator
from .services.image_service import ImageService
from .services.spark_service import SparkService
from .services.text_service import TextService

logger = logging.getLogger("datafog_logger")
logger.setLevel(logging.INFO)


class DataFog:
    """
    Main class for running OCR and text processing pipelines.

    Handles image and text processing operations, including OCR and PII detection.

    Attributes:
        image_service: Service for image processing and OCR.
        text_service: Service for text processing and annotation.
        spark_service: Optional Spark service for distributed processing.
        operations: List of operations to perform.
    """

    def __init__(
        self,
        image_service=ImageService(),
        text_service=TextService(),
        spark_service=None,
        operations: List[OperationType] = [OperationType.ANNOTATE_PII],
    ):
        self.image_service = image_service
        self.text_service = text_service
        self.spark_service: SparkService = spark_service
        self.operations: List[OperationType] = operations
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Initializing DataFog class with the following services and operations:"
        )
        self.logger.info(f"Image Service: {type(image_service)}")
        self.logger.info(f"Text Service: {type(text_service)}")
        self.logger.info(
            f"Spark Service: {type(spark_service) if spark_service else 'None'}"
        )
        self.logger.info(f"Operations: {operations}")

    async def run_ocr_pipeline(self, image_urls: List[str]):
        """
        Run the OCR pipeline asynchronously on a list of images provided via URL.

        This method performs optical character recognition (OCR) on the images specified by the URLs.
        If PII annotation is enabled, it also annotates the extracted text for personally identifiable information.

        Args:
            image_urls (List[str]): A list of URLs pointing to the images to be processed.

        Returns:
            List: If PII annotation is enabled, returns a list of annotated text results.
                  Otherwise, returns a list of extracted text from the images.

        Raises:
            Exception: Any error encountered during the OCR or annotation process.

        Note:
            The method logs various stages of the process, including completion of OCR extraction
            and text annotation, as well as any errors encountered.
        """
        try:
            extracted_text = await self.image_service.ocr_extract(image_urls)
            self.logger.info(f"OCR extraction completed for {len(image_urls)} images.")
            self.logger.debug(
                f"Total length of extracted text: {sum(len(text) for text in extracted_text)}"
            )

            if OperationType.ANNOTATE_PII in self.operations:
                annotated_text = await self.text_service.batch_annotate_text_async(
                    extracted_text
                )
                self.logger.info(
                    f"Text annotation completed with {len(annotated_text)} annotations."
                )
                return annotated_text
            else:
                return extracted_text
        except Exception as e:
            logging.error(f"Error in run_ocr_pipeline: {str(e)}")
            return [f"Error: {str(e)}"]

    async def run_text_pipeline(self, str_list: List[str]):
        """
        Run the text pipeline asynchronously on a list of input text.

        This method processes a list of text strings, potentially annotating them for personally
        identifiable information (PII) if the ANNOTATE_PII operation is enabled.

        Args:
            str_list (List[str]): A list of text strings to be processed.

        Returns:
            List: If PII annotation is enabled, returns a list of annotated text results.
                  Otherwise, returns the original list of text strings.

        Raises:
            Exception: Any error encountered during the text processing or annotation.

        Note:
            The method logs the start of the pipeline, the completion of text annotation if applicable,
            and any errors encountered during processing.
        """
        try:
            self.logger.info(f"Starting text pipeline with {len(str_list)} texts.")
            if OperationType.ANNOTATE_PII in self.operations:
                annotated_text = await self.text_service.batch_annotate_text_async(
                    str_list
                )
                self.logger.info(
                    f"Text annotation completed with {len(annotated_text)} annotations."
                )
                return annotated_text

            self.logger.info("No annotation operation found; returning original texts.")
            return str_list
        except Exception as e:
            self.logger.error(f"Error in run_text_pipeline: {str(e)}")
            raise

    def run_text_pipeline_sync(self, str_list: List[str]):
        """
        Run the text pipeline synchronously on a list of input text.

        This method processes a list of text strings in a synchronous manner, potentially
        annotating them for personally identifiable information (PII) if the ANNOTATE_PII
        operation is enabled.

        Args:
            str_list (List[str]): A list of text strings to be processed.

        Returns:
            List: If PII annotation is enabled, returns a list of annotated text results.
                  Otherwise, returns the original list of text strings.

        Raises:
            Exception: Any error encountered during the text processing or annotation.

        Note:
            The method logs the start of the pipeline, the completion of text annotation if applicable,
            and any errors encountered during processing. This synchronous version may be preferred
            for smaller datasets or when immediate results are required.
        """
        try:
            self.logger.info(f"Starting text pipeline with {len(str_list)} texts.")
            if OperationType.ANNOTATE_PII in self.operations:
                annotated_text = self.text_service.batch_annotate_text_sync(str_list)
                self.logger.info(
                    f"Text annotation completed with {len(annotated_text)} annotations."
                )
                return annotated_text

            self.logger.info("No annotation operation found; returning original texts.")
            return str_list
        except Exception as e:
            self.logger.error(f"Error in run_text_pipeline: {str(e)}")
            raise

    def _add_attributes(self, attributes: dict):
        """
        Add multiple attributes to the DataFog instance.

        This private method allows for the dynamic addition of multiple attributes to the
        DataFog instance. It iterates through the provided dictionary of attributes and
        adds each key-value pair as an attribute.

        Args:
            attributes (dict): A dictionary where keys are attribute names and values are
                               the corresponding attribute values to be added.

        Note:
            This method is intended for internal use and may be used for extending the
            functionality of the DataFog class dynamically. Care should be taken when
            using this method to avoid overwriting existing attributes.
        """
        for key, value in attributes.items():
            pass


class TextPIIAnnotator:
    """
    Class for annotating PII in text.

    Provides functionality to detect and annotate Personally Identifiable Information (PII) in text.

    Attributes:
        text_annotator: SpacyPIIAnnotator instance for text annotation.
        spark_processor: Optional SparkService for distributed processing.
    """

    def __init__(self):
        self.text_annotator = SpacyPIIAnnotator.create()
        self.spark_processor: SparkService = None

    def run(self, text, output_path=None):
        try:
            annotated_text = self.text_annotator.annotate(text)

            # Optionally, output the results to a JSON file
            if output_path:
                with open(output_path, "w") as f:
                    json.dump(annotated_text, f)

            return annotated_text

        finally:
            # Ensure Spark resources are released
            pass
