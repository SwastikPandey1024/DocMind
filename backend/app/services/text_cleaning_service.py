"""Text cleaning and normalization service."""

import logging
import re
import unicodedata
from typing import Optional

logger = logging.getLogger(__name__)


class TextCleaningService:
    """Clean and normalize OCR text."""
    
    # Common header/footer patterns
    HEADER_FOOTER_PATTERNS = [
        r"^page\s+\d+\s*$",
        r"^\d+\s*$",
        r"^[\w\s]*copyright[\w\s]*\d{4}",
        r"^http[s]?://[^\s]+",
        r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$",
    ]
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize unicode characters (NFD decomposition, etc.)."""
        return unicodedata.normalize("NFKD", text)
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace while preserving structure."""
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)
        # Replace multiple newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines).strip()
    
    @staticmethod
    def remove_header_footer(text: str) -> str:
        """Remove common header/footer patterns."""
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Check if line matches header/footer pattern
            is_header_footer = False
            for pattern in TextCleaningService.HEADER_FOOTER_PATTERNS:
                if re.match(pattern, line.lower()):
                    is_header_footer = True
                    break
            
            if not is_header_footer and line.strip():
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    @staticmethod
    def remove_noise(text: str) -> str:
        """Remove noise characters and OCR artifacts."""
        # Remove control characters except newlines and tabs
        text = "".join(char if char.isprintable() or char in "\n\t" else "" for char in text)
        
        # Remove sequences of special characters
        text = re.sub(r"[!@#$%^&*]{3,}", "", text)
        
        # Fix common OCR errors
        replacements = {
            r"l0": "lo",  # lowercase L to O
            r"I0": "IO",  # uppercase I to O
            r"rn": "m",   # r-n to m (context-dependent)
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    @staticmethod
    def remove_duplicate_lines(text: str) -> str:
        """Remove consecutive duplicate lines."""
        lines = text.split("\n")
        cleaned_lines = []
        prev_line = None
        
        for line in lines:
            if line.strip() and line != prev_line:
                cleaned_lines.append(line)
                prev_line = line
            elif not line.strip():
                cleaned_lines.append(line)
                prev_line = None
        
        return "\n".join(cleaned_lines)
    
    def clean_text(
        self,
        text: str,
        remove_headers: bool = True,
        remove_noise: bool = True,
        remove_duplicates: bool = True,
    ) -> str:
        """
        Comprehensive text cleaning.
        
        Args:
            text: Raw OCR text
            remove_headers: Remove header/footer patterns
            remove_noise: Remove noise characters
            remove_duplicates: Remove duplicate lines
            
        Returns:
            Cleaned text
        """
        logger.info("Starting text cleaning")
        
        # Normalize unicode
        text = self.normalize_unicode(text)
        
        # Remove extra whitespace
        text = self.remove_extra_whitespace(text)
        
        # Remove headers/footers
        if remove_headers:
            text = self.remove_header_footer(text)
        
        # Remove noise
        if remove_noise:
            text = self.remove_noise(text)
        
        # Remove duplicate lines
        if remove_duplicates:
            text = self.remove_duplicate_lines(text)
        
        # Final whitespace cleanup
        text = self.remove_extra_whitespace(text)
        
        logger.info("Text cleaning complete")
        return text
