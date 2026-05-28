from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.schemas.procedure import ProcedureSummary, ProcedureDetail, UpdateStatusRequest
from app.internal.database import get_db
from app.internal.models import Tramite, EstadoTramite

router = APIRouter(prefix="/admin", tags=["Administración"])

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Credenciales no válidas")


@router.get("/tramites", response_model=List[ProcedureSummary])
async def list_all_procedures(
        estado: Optional[EstadoTramite] = Query(None),
        current_user: str = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Iniciamos la consulta base sobre la tabla de trámites
    query = db.query(Tramite)

    # Si el administrador envió un filtro por estado en la URL (?estado=en_curso), lo aplicamos
    if estado:
        query = query.filter(Tramite.estado == estado)

    tramites_db = query.all()

    # Adaptamos los objetos de SQLAlchemy al formato Pydantic de ProcedureSummary
    # Nota: Transformamos la fecha a string ISO o dejamos que Pydantic la procese si acepta datetime
    respuesta = []
    for t in tramites_db:
        respuesta.append({
            "uuid": t.uuid,
            "dni": t.dni,
            "tipo": t.tipo.value,
            "estado": t.estado.value,
            "fechaCreacion": t.fecha_creacion
        })

    return respuesta


@router.get("/tramite/{uuid}", response_model=ProcedureDetail)
async def get_procedure_detail(
        uuid: str,
        current_user: str = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Buscamos el trámite por su identificador único en la base de datos
    t = db.query(Tramite).filter(Tramite.uuid == uuid).first()

    if not t:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")

    # Estructuramos la respuesta mapeando dinámicamente los campos según corresponda (ALTA/BAJA)
    return {
        "uuid": t.uuid,
        "tipo": t.tipo.value,
        "dni": t.dni,
        "nombre": t.nombre,
        "apellido": t.apellido,
        "estado": t.estado.value,
        "urlDni": t.url_dni,
        "urlImpuesto": t.url_impuesto,
        "urlFactura": t.url_factura,
        "fechaCreacion": t.fecha_creacion,
        "fechaActualizacion": t.fecha_actualizacion
    }


# Creamos una clase intermedia para recibir el cuerpo del PATCH de acuerdo al Swagger
from pydantic import BaseModel


class UpdateStatusRequest(BaseModel):
    estado: EstadoTramite
    observaciones: Optional[str] = None


@router.patch("/tramite/{uuid}", response_model=dict)
async def change_status(
        uuid: UUID,
        request_data: UpdateStatusRequest,
        current_user: str = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Buscamos el trámite por su UUID nativo en PostgreSQL
    tramite = db.query(Tramite).filter(Tramite.uuid == uuid).first()

    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trámite no encontrado"
        )

    # Regla de negocio / Validación: Si el trámite se rechaza, exigimos observaciones
    if request_data.estado == EstadoTramite.rechazado and not request_data.observaciones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar un comentario/observación indicando el motivo del rechazo."
        )

    # Actualizamos los campos persistentes en la tabla
    tramite.estado = request_data.estado
    tramite.observaciones = request_data.observaciones
    tramite.fecha_actualizacion = datetime.utcnow()  # Registramos la fecha de auditoría

    # Confirmamos los cambios en el contenedor de PostgreSQL
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al guardar los cambios en la base de datos."
        )

    return {"message": f"El trámite ha cambiado exitosamente al estado: {request_data.estado.value}"}