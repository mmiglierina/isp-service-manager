from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class ProcedureStatus(str, Enum):
    in_progress = "en_curso"
    completed = "completado"
    rejected = "rechazado"
    finished = "finalizado"

class CreatedResponse(BaseModel):
    uuid: UUID
    message: str

class ProcedureSummary(BaseModel):
    uuid: UUID
    dni: str
    type: str # ALTA or BAJA
    status: ProcedureStatus
    created_at: datetime

    class Config:
        from_attributes = True

class ProcedureDetail(ProcedureSummary):
    nombre: str
    apellido: str
    email: EmailStr
    archivos: list[str]