from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

# --- ENUMS EN CAPA DE VALIDACIÓN ---
class ProcedureStatus(str, Enum):
    in_progress = "en_curso"
    completed = "completado"
    rejected = "rechazado"
    finished = "finalizado"

# --- RESPUESTAS CLIENTE ---
class CreatedResponse(BaseModel):
    uuid: UUID
    mensaje: str  # Ajustado al Swagger: "mensaje" en español

    class Config:
        from_attributes = True


# --- ESQUEMAS ADMINISTRATIVOS (Mapeados con el Swagger) ---
class ProcedureSummary(BaseModel):
    uuid: UUID
    dni: str
    tipo: str  # ALTA o BAJA
    estado: ProcedureStatus
    fechaCreacion: datetime  # Mapea a la respuesta JSON requerida

    class Config:
        # Permite que Pydantic lea directamente objetos ORM de SQLAlchemy
        # y mapee automáticamente campos si usamos diccionarios intermedios
        from_attributes = True


class ProcedureDetail(BaseModel):
    uuid: UUID
    tipo: str
    dni: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    estado: ProcedureStatus
    urlDni: str
    urlImpuesto: Optional[str] = None
    urlFactura: Optional[str] = None
    fechaCreacion: datetime
    fechaActualizacion: datetime

    class Config:
        from_attributes = True


# --- PETICIONES (Requests) ---
class UpdateStatusRequest(BaseModel):
    """Esquema para validar el cuerpo del PATCH /admin/tramite/{uuid}"""
    estado: ProcedureStatus
    observaciones: Optional[str] = None