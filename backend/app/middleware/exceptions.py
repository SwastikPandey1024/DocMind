import logging
import uuid
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Global exception handler middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Handle exceptions and return standardized error responses."""
        
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
            
        except SQLAlchemyError as e:
            logger.error(
                f"Database error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                }
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Database error occurred",
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )
            
        except ValueError as e:
            logger.warning(
                f"Validation error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                }
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "message": str(e),
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )
            
        except Exception as e:
            logger.exception(
                f"Unhandled exception",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )


def setup_exceptions(app: FastAPI) -> None:
    """Register exception handling middleware."""
    app.add_middleware(ExceptionMiddleware)
