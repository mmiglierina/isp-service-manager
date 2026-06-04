from fastapi import APIRouter, UploadFile, File, Form, status, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import uuid

from app.schemas.procedure import CreatedResponse
from app.services.file_manager import validate_and_save_file

from app.internal.database import get_db
from app.internal.models import Tramite, TipoTramite, EstadoTramite

router = APIRouter(prefix="/tramite", tags=["Clientes"])

@router.post("/alta", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_activation(
        nombre: str = Form(...),
        apellido: str = Form(...),
        dni: str = Form(...),
        email: str = Form(...),
        adjuntoDni: UploadFile = File(...),
        adjuntoImpuesto: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Regla 1: Verificar si ya tiene un trámite activo (en_curso)
    tramite_activo = db.query(Tramite).filter(
        Tramite.dni == dni,
        Tramite.estado == EstadoTramite.en_curso
    ).first()

    if tramite_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un trámite en curso para el DNI {dni}. Debe esperar a que finalice."
        )

    # Procesar y validar archivos con tu servicio seguro
    path_dni = validate_and_save_file(adjuntoDni, "dni")
    path_impuesto = validate_and_save_file(adjuntoImpuesto, "taxes")

    # Generamos el UUID string compatible con la columna de la BD
    generated_uuid = uuid.uuid4()

    # Creamos el registro usando el modelo ORM de SQLAlchemy
    nuevo_tramite = Tramite(
        uuid=generated_uuid,
        tipo=TipoTramite.ALTA,
        dni=dni,
        nombre=nombre,
        apellido=apellido,
        email=email,
        url_dni=path_dni,
        url_impuesto=path_impuesto,
        estado=EstadoTramite.en_curso
    )

    # Impactamos en la base de datos real
    db.add(nuevo_tramite)
    db.commit()

    return {
        "uuid": generated_uuid,
        "mensaje": "Alta iniciada correctamente."
    }

@router.post("/baja", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_deactivation(
        dni: str = Form(...),
        adjuntoDni: UploadFile = File(...),
        adjuntoFactura: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Regla 1: Verificar si ya tiene un trámite activo en curso
    tramite_activo = db.query(Tramite).filter(
        Tramite.dni == dni,
        Tramite.estado == EstadoTramite.en_curso
    ).first()

    if tramite_activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un trámite en curso para el DNI {dni}. Debe esperar a que finalice."
        )

    # Regla 2: Verificamos si existe un trámite de ALTA para este DNI que esté COMPLETADO
    alta_existente = db.query(Tramite).filter(
        Tramite.dni == dni,
        Tramite.tipo == TipoTramite.ALTA,
        Tramite.estado == EstadoTramite.completado
    ).first()

    if not alta_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede iniciar el trámite de baja. No existe ningún servicio de alta activo para el DNI proporcionado."
        )

    # Procesamos los archivos normalmente
    path_dni = validate_and_save_file(adjuntoDni, "deactivation_dni")
    path_invoice = validate_and_save_file(adjuntoFactura, "deactivation_invoice")

    generated_uuid = uuid.uuid4()

    # SOLUCIÓN: Creamos la entidad mapeando el DNI, pero arrastrando NOMBRE y APELLIDO del alta original
    nuevo_tramite = Tramite(
        uuid=generated_uuid,
        tipo=TipoTramite.BAJA,
        dni=dni,
        nombre=alta_existente.nombre,
        apellido=alta_existente.apellido,
        email=alta_existente.email,
        url_dni=path_dni,
        url_factura=path_invoice,
        estado=EstadoTramite.en_curso
    )

    db.add(nuevo_tramite)
    db.commit()

    return {
        "uuid": generated_uuid,
        "mensaje": "Baja iniciada correctamente."
    }

@router.get("/{uuid}", status_code=status.HTTP_200_OK)
async def get_procedure_status(uuid: UUID, db: Session = Depends(get_db)):
    # Buscamos el trámite directamente en la base de datos por su clave primaria (UUID)
    tramite = db.query(Tramite).filter(Tramite.uuid == uuid).first()

    # Si no existe en la base de datos, disparamos el error 404 estandarizado
    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trámite no encontrado. Verifique el UUID e intente nuevamente."
        )

    # Retornamos la información incluyendo el tipo de trámite (ALTA o BAJA)
    return {
        "uuid": tramite.uuid,
        "tipo": tramite.tipo.value if hasattr(tramite.tipo, 'value') else tramite.tipo,
        "estado": tramite.estado.value if hasattr(tramite.estado, 'value') else tramite.estado,
        "observaciones": tramite.observaciones if hasattr(tramite, 'observaciones') else None
    }