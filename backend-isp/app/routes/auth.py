from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.internal import models
from app.internal.database import get_db
from app.services.auth import verify_password, generar_tokens_login

router = APIRouter(prefix="/auth", tags=["Seguridad"])

class LoginRequest(BaseModel):
    usuario: str
    password: str

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Buscamos al administrador en PostgreSQL (reemplazando al viejo MOCK_ADMIN)
    admin_user = db.query(models.UsuarioAdmin).filter(models.UsuarioAdmin.username == request.usuario).first()

    # 2. Validamos existencia y hash
    if not admin_user or not verify_password(request.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Invocamos la función del servicio que procesa los tokens con las variables del .env
    return generar_tokens_login(username=admin_user.username)