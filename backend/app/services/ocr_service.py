"""OCR Service using PyMuPDF and PaddleOCR"""

import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import fitz
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class OCRBlock:
    """Single OCR block from a document."""
    page_number: int
    block_index: int
    text: str
    confidence: float
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    block_type: str  # "text", "table", "image", etc.
    reading_order: int


@dataclass
class OCRPage:
    """All OCR blocks from a single page."""
    page_number: int
    total_blocks: int
    blocks: list[OCRBlock]
    page_text: str
    detected_language: str


class OCRService:
    """OCR pipeline with PyMuPDF and PaddleOCR."""
    
    def __init__(self, languages: list[str] = ["en"]):
        """
        Initialize OCR service.
        
        Args:
            languages: Languages to detect. Default: ["en"]
        """
        self.languages = languages
        language = languages[0] if languages else "en"
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=language,
            use_gpu=False,  # Set to True if GPU available
            show_log=False,
        )
        self.confidence_threshold = 0.3
    
    def extract_from_pdf(self, pdf_path: str | Path) -> list[OCRPage]:
        """
        Extract OCR from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of OCRPage objects, one per page
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Starting OCR extraction: {pdf_path}")
        ocr_pages = []
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            logger.info(f"PDF has {total_pages} pages")
            
            for page_num in range(total_pages):
                try:
                    page = doc[page_num]
                    
                    # Render page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    image_bytes = pix.tobytes("ppm")
                    image = Image.open(io.BytesIO(image_bytes))
                    image_array = np.array(image)
                    
                    # Convert RGB to BGR for OpenCV
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    
                    # Run OCR on page
                    ocr_result = self.ocr.ocr(image_bgr, cls=True)
                    
                    # Parse results
                    page_blocks = []
                    page_text_parts = []
                    
                    if ocr_result and ocr_result[0]:
                        for block_idx, line in enumerate(ocr_result[0]):
                            if len(line) < 2:
                                continue
                            
                            # Extract text and confidence
                            points = line[0]
                            text = line[1][0]
                            confidence = float(line[1][1])
                            
                            # Filter by confidence
                            if confidence < self.confidence_threshold:
                                logger.debug(f"Skipping low-confidence text (conf={confidence}): {text[:50]}")
                                continue
                            
                            # Convert points to bbox
                            points_array = np.array(points, dtype=np.float32)
                            x_coords = points_array[:, 0]
                            y_coords = points_array[:, 1]
                            bbox = (float(x_coords.min()), float(y_coords.min()), 
                                   float(x_coords.max()), float(y_coords.max()))
                            
                            block = OCRBlock(
                                page_number=page_num,
                                block_index=block_idx,
                                text=text,
                                confidence=confidence,
                                bbox=bbox,
                                block_type="text",
                                reading_order=block_idx,
                            )
                            page_blocks.append(block)
                            page_text_parts.append(text)
                    
                    # Create page result
                    page_text = " ".join(page_text_parts)
                    ocr_page = OCRPage(
                        page_number=page_num,
                        total_blocks=len(page_blocks),
                        blocks=page_blocks,
                        page_text=page_text,
                        detected_language=self.languages[0],
                    )
                    ocr_pages.append(ocr_page)
                    
                    logger.info(f"Extracted page {page_num + 1}/{total_pages}: {len(page_blocks)} blocks")
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    raise
            
            doc.close()
            logger.info(f"OCR extraction complete: {len(ocr_pages)} pages")
            return ocr_pages
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
    
    def extract_from_image(self, image_path: str | Path) -> list[OCRBlock]:
        """
        Extract OCR from single image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of OCRBlock objects
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Running OCR on image: {image_path}")
        
        # Load image
        image = Image.open(image_path)
        image_array = np.array(image)
        
        # Convert to BGR if RGB
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array
        
        # Run OCR
        ocr_result = self.ocr.ocr(image_bgr, cls=True)
        
        # Parse results
        blocks = []
        if ocr_result and ocr_result[0]:
            for block_idx, line in enumerate(ocr_result[0]):
                if len(line) < 2:
                    continue
                
                points = line[0]
                text = line[1][0]
                confidence = float(line[1][1])
                
                if confidence < self.confidence_threshold:
                    continue
                
                # Convert points to bbox
                points_array = np.array(points, dtype=np.float32)
                x_coords = points_array[:, 0]
                y_coords = points_array[:, 1]
                bbox = (float(x_coords.min()), float(y_coords.min()), 
                       float(x_coords.max()), float(y_coords.max()))
                
                block = OCRBlock(
                    page_number=0,
                    block_index=block_idx,
                    text=text,
                    confidence=confidence,
                    bbox=bbox,
                    block_type="text",
                    reading_order=block_idx,
                )
                blocks.append(block)
        
        logger.info(f"Image OCR complete: {len(blocks)} blocks")
        return blocks
