"""Middleware setup."""

from fastapi import FastAPI

from app.middleware.cors import setup_cors
from app.middleware.exceptions import setup_exceptions
from app.middleware.logging import setup_request_logging

__all__ = ["setup_cors", "setup_exceptions", "setup_request_logging"]
