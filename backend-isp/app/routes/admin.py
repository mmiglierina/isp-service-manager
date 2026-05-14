from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from app.schemas.procedure import ProcedureSummary, ProcedureDetail, ProcedureStatus
from typing import List
from app.internal.mock_db import get_all, update_status

router = APIRouter(prefix="/admin", tags=["Administración"])

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials # Aquí extraemos el string del token
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Credenciales no válidas")

@router.get("/tramites", response_model=List[ProcedureSummary])
async def list_all_procedures(current_user: str = Depends(get_current_user)):
    # TODO: Aquí se conectarían los datos de la base de datos.
    # Por ahora devolvemos una lista de ejemplo protegida.
    return get_all()

@router.get("/tramite/{uuid}", response_model=ProcedureDetail)
async def get_procedure_detail(uuid: str, current_user: str = Depends(get_current_user)):
    for t in get_all():
        if str(t["uuid"]) == uuid:
            return t
    raise HTTPException(status_code=404, detail="Trámite no encontrado")

@router.patch("/tramite/{uuid}")
async def change_status(uuid: str, status: str, current_user: str = Depends(get_current_user)):
    if update_status(uuid, status):
        return {"message": "Estado actualizado"}
    raise HTTPException(status_code=404, detail="Trámite no encontrado")