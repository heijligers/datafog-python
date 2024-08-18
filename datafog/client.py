# client.py

import asyncio
import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from pydantic import BaseModel
from rich import print
from rich.progress import track

from .config import get_config
from .main import DataFog
from .models.spacy_nlp import SpacyAnnotator

app = typer.Typer()


@app.command()
def scan_image(
    image_urls: List[str] = typer.Argument(
        None, help="List of image URLs or file paths to extract text from"
    ),
    operations: str = typer.Option("annotate_pii", help="Operation to perform"),
):
    """Extract text from images."""
    if not image_urls:
        typer.echo("No image URLs or file paths provided. Please provide at least one.")
        raise typer.Exit(code=1)

    logging.basicConfig(level=logging.INFO)
    ocr_client = DataFog(operations=operations)
    try:
        results = asyncio.run(ocr_client.run_ocr_pipeline(image_urls=image_urls))
        typer.echo(f"OCR Pipeline Results: {results}")
    except Exception as e:
        logging.exception("Error in run_ocr_pipeline")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def scan_text(
    str_list: List[str] = typer.Argument(
        None, help="List of texts to extract text from"
    ),
    operations: str = typer.Option("annotate_pii", help="Operation to perform"),
):
    """Annotate texts to detect PII entities."""
    if not str_list:
        typer.echo("No texts provided.")
        raise typer.Exit(code=1)

    logging.basicConfig(level=logging.INFO)
    text_client = DataFog(operations=operations)
    try:
        results = asyncio.run(text_client.run_text_pipeline(str_list=str_list))
        typer.echo(f"Text Pipeline Results: {results}")
    except Exception as e:
        logging.exception("Text pipeline error")
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)


@app.command()
def health():
    """Check DataFog service health."""
    typer.echo("DataFog is running.")


@app.command()
def show_config():
    """Show current configuration."""
    typer.echo(get_config())


@app.command()
def download_model(model_name: str = typer.Argument(..., help="Model to download")):
    """Download a model."""
    SpacyAnnotator.download_model(model_name)
    typer.echo(f"Model {model_name} downloaded.")


@app.command()
def show_spacy_model_directory(
    model_name: str = typer.Argument(..., help="Model to check")
):
    """Show model path."""
    annotator = SpacyAnnotator(model_name)
    typer.echo(annotator.show_model_path())


@app.command()
def list_spacy_models():
    """List available models."""
    annotator = SpacyAnnotator()
    typer.echo(annotator.list_models())


@app.command()
def list_entities():
    """List available entities."""
    annotator = SpacyAnnotator()
    typer.echo(annotator.list_entities())


if __name__ == "__main__":
    app()
