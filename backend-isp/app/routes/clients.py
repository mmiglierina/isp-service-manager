from fastapi import APIRouter, UploadFile, File, Form, status
from app.schemas.procedure import CreatedResponse, ProcedureStatus
from app.services.file_manager import validate_and_save_file
import uuid
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.internal.mock_db import add_tramite

router = APIRouter(prefix="/procedure", tags=["Clientes"])

@router.post("/alta", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_activation(
        nombre: str = Form(...),
        apellido: str = Form(...),
        dni: str = Form(...),
        email: str = Form(...),
        adjuntoDni: UploadFile = File(...),
        adjuntoImpuesto: UploadFile = File(...)
):
    # Process files using our secure service
    path_dni = validate_and_save_file(adjuntoDni, "dni")
    path_impuesto = validate_and_save_file(adjuntoImpuesto, "taxes")

    # Generamos el ID único
    generated_uuid = str(uuid.uuid4())

    nuevo_tramite = {
        "uuid": generated_uuid,
        "dni": dni,
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "type": "ALTA",
        "status": "en_curso",
        "created_at": datetime.now(),
        "archivos": [path_dni, path_impuesto]
    }

    # 3. Lo guardamos en la lista global (Memoria)
    add_tramite(nuevo_tramite)

    return {
        "uuid": generated_uuid,
        "message": "Activation process initiated. Files uploaded successfully."
    }

@router.post("/baja", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_deactivation(
        dni: str = Form(...),
        nroServicio: str = Form(...),
        adjuntoDni: UploadFile = File(...),
        adjuntoFactura: UploadFile = File(...)
):
    # Validation and saving of files using our secure service
    # This addresses QA standards for integrity and security
    path_dni = validate_and_save_file(adjuntoDni, "deactivation_dni")
    path_invoice = validate_and_save_file(adjuntoFactura, "deactivation_invoice")

    # TODO: In a real-world scenario, you would save these details in a database
    generated_uuid = uuid.uuid4()

    return {
        "uuid": generated_uuid,
        "message": "Deactivation process initiated. Files processed successfully."
    }

# Mock data for demonstration purposes (QA standard: testing with structured data)
# In a real project, this data would come from your database
MOCK_PROCEDURES = {
    "d0e12345-e89b-12d3-a456-426614174000": {
        "status": ProcedureStatus.in_progress,
        "observations": "Documents received and under review by the ISP team."
    }
}

@router.get("/{uuid}", status_code=status.HTTP_200_OK)
async def get_procedure_status(uuid: UUID):
    # Search for the procedure in our data source
    procedure_id = str(uuid)

    if procedure_id not in MOCK_PROCEDURES:
        # Standard QA practice: Return 404 if the resource is not found as per Swagger
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure not found with the provided UUID."
        )

    return MOCK_PROCEDURES[procedure_id]