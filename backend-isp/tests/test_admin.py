import pytest
from uuid import uuid4
from app.internal.models import Tramite, TipoTramite, EstadoTramite

# ==============================================================================
# 1. TESTS PARA LISTAR TRÁMITES (GET /admin/tramites)
# ==============================================================================
@pytest.mark.asyncio
async def test_listar_todos_los_tramites(admin_client, db_session):
    """Verifica que el admin pueda listar todos los trámites sin filtros."""

    # ARRANGE: Poblamos la base de datos de test
    tramite_1 = Tramite(
        uuid=uuid4(), tipo=TipoTramite.ALTA, dni="11223344",
        estado=EstadoTramite.en_curso, url_dni="http://test.com/dni1.pdf"
    )
    tramite_2 = Tramite(
        uuid=uuid4(), tipo=TipoTramite.BAJA, dni="55667788",
        estado=EstadoTramite.completado, url_dni="http://test.com/dni2.pdf"
    )
    db_session.add_all([tramite_1, tramite_2])
    db_session.commit()

    # ACT: Consumimos el endpoint usando el cliente autenticado
    response = await admin_client.get("/admin/tramites")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Validamos que respete el formato camelCase del esquema ProcedureSummary
    assert data[0]["dni"] == "11223344"
    assert "fechaCreacion" in data[0]

@pytest.mark.asyncio
async def test_filtrar_tramites_por_estado(admin_client, db_session):
    """Verifica que funcione el query param de filtrado (?estado=...)."""

    # ARRANGE: Creamos uno en curso y otro completado
    t_en_curso = Tramite(
        uuid=uuid4(), tipo=TipoTramite.ALTA, dni="1111",
        estado=EstadoTramite.en_curso, url_dni="http://test.com/1.pdf"
    )
    t_completado = Tramite(
        uuid=uuid4(), tipo=TipoTramite.BAJA, dni="2222",
        estado=EstadoTramite.completado, url_dni="http://test.com/2.pdf"
    )
    db_session.add_all([t_en_curso, t_completado])
    db_session.commit()

    # ACT: Solicitamos filtrar solo por los que están 'en_curso'
    response = await admin_client.get("/admin/tramites?estado=en_curso")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["dni"] == "1111"
    assert data[0]["estado"] == "en_curso"

# ==============================================================================
# 2. TESTS PARA DETALLE DE UN TRÁMITE (GET /admin/tramite/{uuid})
# ==============================================================================
@pytest.mark.asyncio
async def test_obtener_detalle_tramite_exitoso(admin_client, db_session):
    """Verifica la obtención de datos extendidos de un trámite específico."""
    # ARRANGE
    target_uuid = uuid4()
    tramite = Tramite(
        uuid=target_uuid,
        tipo=TipoTramite.ALTA,
        dni="33445566",
        nombre="Juan",
        apellido="Pérez",
        estado=EstadoTramite.en_curso,
        url_dni="http://test.com/dni.pdf",
        url_impuesto="http://test.com/impuesto.pdf"
    )
    db_session.add(tramite)
    db_session.commit()

    # ACT
    response = await admin_client.get(f"/admin/tramite/{target_uuid}")

    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == str(target_uuid)
    assert data["nombre"] == "Juan"
    assert data["apellido"] == "Pérez"
    assert data["urlImpuesto"] == "http://test.com/impuesto.pdf"

@pytest.mark.asyncio
async def test_detalle_tramite_inexistente_devuelve_404(admin_client):
    """Verifica que devuelva un 404 Not Found si el UUID no existe."""
    random_uuid = uuid4()

    response = await admin_client.get(f"/admin/tramite/{random_uuid}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trámite no encontrado"


# ==============================================================================
# 3. TESTS PARA ACTUALIZACIÓN DE ESTADO (PATCH /admin/tramite/{uuid})
# ==============================================================================
@pytest.mark.asyncio
async def test_cambio_estado_exitoso(admin_client, db_session):
    """Verifica la transición de estado correcta en la base de datos."""
    # ARRANGE
    target_uuid = uuid4()
    tramite = Tramite(
        uuid=target_uuid, tipo=TipoTramite.ALTA, dni="123456",
        estado=EstadoTramite.en_curso, url_dni="http://test.com/dni.pdf"
    )
    db_session.add(tramite)
    db_session.commit()

    payload = {
        "estado": "completado",
        "observaciones": "Todo en orden, documento validado."
    }

    # ACT
    response = await admin_client.patch(f"/admin/tramite/{target_uuid}", json=payload)

    # ASSERT
    assert response.status_code == 200
    assert "El trámite ha cambiado exitosamente" in response.json()["message"]

    # Verificación en Base de Datos para asegurar la persistencia real
    db_session.refresh(tramite)
    assert tramite.estado == EstadoTramite.completado
    assert tramite.observaciones == "Todo en orden, documento validado."

@pytest.mark.asyncio
async def test_cambio_estado_rechazado_sin_observaciones_error_400(admin_client, db_session):
    """Valida si se rechaza, las observaciones son obligatorias."""
    # ARRANGE
    target_uuid = uuid4()
    tramite = Tramite(
        uuid=target_uuid, tipo=TipoTramite.ALTA, dni="123456",
        estado=EstadoTramite.en_curso, url_dni="http://test.com/dni.pdf"
    )
    db_session.add(tramite)
    db_session.commit()

    # Payload inválido por omitir o mandar vacías las observaciones en un rechazo
    payload = {
        "estado": "rechazado",
        "observaciones": ""
    }

    # ACT
    response = await admin_client.patch(f"/admin/tramite/{target_uuid}", json=payload)

    # ASSERT
    assert response.status_code == 400
    assert "Debe proporcionar un comentario/observación" in response.json()["detail"]

    # Nos aseguramos de que el estado en la BD NO haya cambiado
    db_session.refresh(tramite)
    assert tramite.estado == EstadoTramite.en_curso