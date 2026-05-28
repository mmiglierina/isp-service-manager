import pytest
import io
import uuid
from app.internal.models import Tramite, TipoTramite, EstadoTramite

# ==============================================================================
# Helpers para simular archivos PDF/Imágenes en memoria RAM
# ==============================================================================
def crear_archivo_mock(nombre_archivo: str) -> tuple:
    """Genera un archivo binario simulado en memoria para los uploads."""
    return (nombre_archivo, io.BytesIO(b"contenido_de_prueba_pdf_o_imagen"), "application/pdf")

# ==============================================================================
# 1. TEST DEL TRÁMITE DE ALTA (Exitoso)
# ==============================================================================
@pytest.mark.asyncio
async def test_crear_tramite_alta_exitoso(client):
    """Verifica que un cliente pueda iniciar su trámite de Alta correctamente."""

    # 1. ARRANGE: Preparamos los textos del formulario y los archivos adjuntos
    form_data = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "email": "juan@example.com"
    }

    archivos = {
        "adjuntoDni": crear_archivo_mock("dni_juan.pdf"),
        "adjuntoImpuesto": crear_archivo_mock("impuesto_juan.pdf")
    }

    # 2. ACT: Enviamos la petición POST simulando form-data al endpoint correcto
    response = await client.post("/tramite/alta", data=form_data, files=archivos)

    # 3. ASSERT: Validamos la respuesta del servidor
    assert response.status_code == 201
    data = response.json()
    assert "uuid" in data
    assert data["mensaje"] == "Alta iniciada correctamente."

# ==============================================================================
# 2. TESTS DEL TRÁMITE DE BAJA (Filtro de Negocio y Éxito)
# ==============================================================================
@pytest.mark.asyncio
async def test_crear_tramite_baja_fallido_sin_alta_previa(client):
    """Regra de negocio: No se puede iniciar una baja si el DNI no tiene un alta completada."""

    form_data = {
        "dni": "99999999"  # Un DNI random que no existe en la BD en memoria
    }
    archivos = {
        "adjuntoDni": crear_archivo_mock("baja_dni.pdf"),
        "adjuntoFactura": crear_archivo_mock("baja_factura.pdf")
    }

    response = await client.post("/tramite/baja", data=form_data, files=archivos)

    # Debe rebotar con un 400 Bad Request debido a tu validación interna
    assert response.status_code == 400
    assert "No se puede iniciar el trámite de baja" in response.json()["detail"]


@pytest.mark.asyncio
async def test_crear_tramite_baja_exitoso(client, db_session):
    """Verifica que si el DNI posee un alta 'completado', permita procesar la baja."""

    # 1. ARRANGE: Forzamos la preexistencia de un Alta Completada en la BD mock
    dni_cliente = "45123456"
    alta_existente = Tramite(
        tipo=TipoTramite.ALTA,
        dni=dni_cliente,
        nombre="Carlos",
        apellido="Gómez",
        email="carlos@example.com",
        url_dni="uploads/dni.pdf",
        url_impuesto="uploads/tax.pdf",
        estado=EstadoTramite.completado  # Estado requerido para habilitar la baja
    )
    db_session.add(alta_existente)
    db_session.commit()

    # Preparamos los datos de la baja para ese mismo DNI
    form_data = {"dni": dni_cliente}
    archivos = {
        "adjuntoDni": crear_archivo_mock("baja_dni_carlos.pdf"),
        "adjuntoFactura": crear_archivo_mock("baja_factura_carlos.pdf")
    }

    # 2. ACT: Solicitamos la baja
    response = await client.post("/tramite/baja", data=form_data, files=archivos)

    # 3. ASSERT: Ahora sí debe permitir el inicio del trámite
    assert response.status_code == 201
    assert response.json()["mensaje"] == "Baja iniciada correctamente."


# ==============================================================================
# 3. TESTS DE OBTENER TRÁMITE (GET)
# ==============================================================================
@pytest.mark.asyncio
async def test_obtener_tramite_existente(client, db_session):
    """Verifica la consulta de estado de un trámite existente mediante su UUID."""

    # 1. ARRANGE: Generamos un objeto UUID real de Python
    uuid_testigo = uuid.UUID("fa9b77fa-b39b-4654-8c01-7fa7dfce92e0")

    # Se lo pasamos directamente al modelo
    tramite_testigo = Tramite(
        uuid=uuid_testigo,
        tipo=TipoTramite.ALTA,
        dni="88888888",
        nombre="Luis",
        apellido="Sanz",
        url_dni="uploads/test_dni_luis.pdf",
        url_impuesto="uploads/test_impuesto_luis.pdf",
        estado=EstadoTramite.en_curso
    )
    db_session.add(tramite_testigo)
    db_session.commit()

    # 2. ACT: Al endpoint sí le pasamos el string en la URL (FastAPI lo parsea solo)
    response = await client.get(f"/tramite/{str(uuid_testigo)}")

    # 3. ASSERT: Validamos la respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == str(uuid_testigo)  # FastAPI responde con texto en el JSON
    assert data["tipo"] == "ALTA"
    assert data["estado"] == "en_curso"


@pytest.mark.asyncio
async def test_obtener_tramite_no_encontrado(client):
    """Verifica que si el UUID no figura en el sistema, devuelva un error 404."""

    uuid_inexistente = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/tramite/{uuid_inexistente}")

    assert response.status_code == 404
    assert "Trámite no encontrado" in response.json()["detail"]