import logging

import pytesseract
from PIL import Image


class PytesseractProcessor:
    async def extract_text_from_image(self, image: Image.Image) -> str:
        try:
            return pytesseract.image_to_string(image)
        except Exception as e:
            logging.error(f"Pytesseract error: {str(e)}")
            raise
