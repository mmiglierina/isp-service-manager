from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.auth import create_access_token, verify_password, get_password_hash
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Seguridad"])

# Mock Administrative User para pruebas de QA / Desarrollo
MOCK_ADMIN = {
    "username": "admin",
    "password": get_password_hash("admin")
}


class LoginRequest(BaseModel):
    usuario: str
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    # Verificación de usuario y contraseña
    if request.usuario != MOCK_ADMIN["username"] or not verify_password(request.password, MOCK_ADMIN["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Calculamos tiempos de expiración reales para cumplir el Swagger
    expires_delta = timedelta(minutes=30)
    expires_at = datetime.utcnow() + expires_delta

    # Generamos los tokens correspondientes
    access_token = create_access_token(data={"sub": request.usuario}, expires_delta=expires_delta)
    refresh_token = create_access_token(data={"sub": request.usuario}, expires_delta=timedelta(days=7))

    # Retornamos la estructura exacta exigida por el Swagger de tu ISP
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresAt": expires_at.isoformat() + "Z"
    }