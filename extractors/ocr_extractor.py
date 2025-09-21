# extractors/ocr_extractor.py

import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import cv2
import numpy as np
import tempfile
import os

def extract_tables_ocr(pdf_path, dpi=300, max_pages=5):
    """
    Extracts tables from scanned PDFs using OCR (Tesseract + OpenCV).
    Returns a list of pandas DataFrames.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(pdf_path, dpi=dpi, output_folder=temp_dir, first_page=1, last_page=max_pages)
            dataframes = []

            for i, image in enumerate(images):
                # Convert PIL image to OpenCV format
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Optional: preprocess image (thresholding, denoising)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

                # Detect contours (potential table cells)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Extract bounding boxes and sort top-to-bottom
                boxes = [cv2.boundingRect(c) for c in contours]
                boxes = sorted(boxes, key=lambda b: b[1])  # sort by y-coordinate

                rows = []
                for box in boxes:
                    x, y, w, h = box
                    roi = img_cv[y:y+h, x:x+w]
                    text = pytesseract.image_to_string(roi, config='--psm 6').strip()
                    if text:
                        rows.append([text])  # crude row; refine later

                # Convert to DataFrame
                if rows:
                    df = pd.DataFrame(rows)
                    dataframes.append(df)

            return dataframes

    except Exception as e:
        print(f"❌ OCR extraction failed for {pdf_path}: {e}")
        return []