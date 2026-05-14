from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.auth import create_access_token, verify_password, get_password_hash
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Seguridad"])

# Mock Administrative User for QA testing
MOCK_ADMIN = {
    "username": "admin",
    "password": get_password_hash("admin")  # Standard hash for security
}

class LoginRequest(BaseModel):
    usuario: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    # Verify user existence and password
    if request.usuario != MOCK_ADMIN["username"] or not verify_password(request.password, MOCK_ADMIN["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": request.usuario})

    return {
        "accessToken": access_token,
        "token_type": "bearer",
        "message": "Authentication successful"
    }