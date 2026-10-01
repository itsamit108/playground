"""Auth endpoints: register, login, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, SessionDep, SettingsDep
from app.schemas.common import RegisterRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(body: RegisterRequest, session: SessionDep) -> UserResponse:
    user = auth_service.register_user(
        session, username=body.username, email=body.email, password=body.password
    )
    return UserResponse.model_validate(user, from_attributes=True)


@router.post("/login", response_model=TokenResponse, summary="Authenticate, get JWT")
def login(
    session: SessionDep,
    settings: SettingsDep,
    form: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    token = auth_service.authenticate(
        session, settings, username=form.username, password=form.password
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user, from_attributes=True)
