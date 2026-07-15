from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer


from app.api.v1.schemas.common import ApiResponse
from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.schemas import (
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# Rate limiting placeholder (NOT implemented): mount per-route limiter dependency here later.
# Keeping it as a comment to avoid introducing new runtime behavior.

_bearer = HTTPBearer(auto_error=False)


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Duplicate email"},
        422: {"description": "Validation error"},
    },
)
def register(

    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[UserResponse]:
    user = auth_service.register(payload)
    return ApiResponse(message="User registered successfully.", data=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    responses={
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
    },
)
def login(

    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[TokenResponse]:
    tokens = auth_service.login(payload)
    return ApiResponse(message="Login successful.", data=tokens)


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    responses={
        401: {"description": "Invalid refresh token"},
        422: {"description": "Validation error"},
    },
)
def refresh_token(

    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[TokenResponse]:
    tokens = auth_service.refresh(payload)
    return ApiResponse(message="Token refreshed successfully.", data=tokens)


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    # Swagger alignment: force security scheme display.
    responses={
        401: {"description": "Missing/invalid token"},
        422: {"description": "Validation error"},
    },
)
def me(
    current_user: User = Depends(get_current_user),
    # unused variable: present to bind auth scheme in OpenAPI/Swagger
    _credentials=Depends(_bearer),
) -> ApiResponse[UserResponse]:
    return ApiResponse(
        message="Current user retrieved successfully.",
        data=UserResponse.model_validate(current_user),
    )



@router.post("/logout", response_model=ApiResponse[MessageResponse])
def logout() -> ApiResponse[MessageResponse]:
    return ApiResponse(
        message="Logout successful.",
        data=MessageResponse(message="Discard access and refresh tokens on the client."),
    )
