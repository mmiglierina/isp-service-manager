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
        nroServicio: str = Form(...),
        adjuntoDni: UploadFile = File(...),
        adjuntoFactura: UploadFile = File(...),
        db: Session = Depends(get_db)  # <-- Inyección de la Base de Datos
):
    # Procesamiento seguro de los adjuntos para la baja
    path_dni = validate_and_save_file(adjuntoDni, "deactivation_dni")
    path_invoice = validate_and_save_file(adjuntoFactura, "deactivation_invoice")

    generated_uuid = uuid.uuid4()

    # Construimos la entidad mapeando los campos nulos correspondientes a BAJA
    nuevo_tramite = Tramite(
        uuid=generated_uuid,
        tipo=TipoTramite.BAJA,
        dni=dni,
        nro_servicio=nroServicio,
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
    tramite = db.query(Tramite).filter(Tramite.uuid == str(uuid)).first()

    # Si no existe en la base de datos, disparamos el error 404 estandarizado
    if not tramite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el trámite buscado con el UUID proporcionado."
        )

    # Devolvemos la estructura exacta que pide el Swagger para el cliente
    return {
        "estado": tramite.estado.value,
        "observaciones": tramite.observaciones
    }