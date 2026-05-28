import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.internal.database import Base
import enum


class TipoTramite(str, enum.Enum):
    ALTA = "ALTA"
    BAJA = "BAJA"


class EstadoTramite(str, enum.Enum):
    en_curso = "en_curso"
    completado = "completado"
    rechazado = "rechazado"
    finalizado = "finalizado"


class Tramite(Base):
    __tablename__ = "tramites"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tipo = Column(Enum(TipoTramite), nullable=False)
    dni = Column(String, nullable=False, index=True)
    estado = Column(Enum(EstadoTramite), default=EstadoTramite.en_curso, nullable=False)

    nombre = Column(String, nullable=True)
    apellido = Column(String, nullable=True)
    email = Column(String, nullable=True)

    nro_servicio = Column(String, nullable=True)

    url_dni = Column(String, nullable=False)
    url_impuesto = Column(String, nullable=True)
    url_factura = Column(String, nullable=True)

    observaciones = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UsuarioAdmin(Base):
    __tablename__ = "usuarios_admin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)