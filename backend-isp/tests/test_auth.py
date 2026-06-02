import pytest
from app.internal.models import UsuarioAdmin
# Importamos la función de hasheo para guardar la contraseña encriptada en la BD de test
from app.services.auth import get_password_hash  # Ajustá la importación según dónde esté en tu app


# ==============================================================================
# 1. SUCCESSFUL LOGIN TEST
# ==============================================================================
@pytest.mark.asyncio
async def test_login_exitoso(client, db_session):
    """Verifica que un administrador con credenciales correctas obtenga sus tokens."""

    # 1. ARRANGE: Creamos un usuario administrador de prueba en la BD en memoria
    target_username = "admin_test"
    target_password = "password_secreta_123"

    hashed_password = get_password_hash(target_password)

    admin_mock = UsuarioAdmin(
        username=target_username,
        hashed_password=hashed_password
    )
    db_session.add(admin_mock)
    db_session.commit()

    # Payload, pero manteniendo las llaves "usuario" y "password" que espera tu API
    login_payload = {
        "usuario": target_username,
        "password": target_password
    }

    # 2. ACT: Enviamos la petición POST al endpoint de login
    response = await client.post("/auth/login", json=login_payload)

    # 3. ASSERT: Validamos que devuelva 200 OK y las claves del token
    assert response.status_code == 200

    response_data = response.json()

    assert "accessToken" in response_data
    assert "refreshToken" in response_data
    assert "expiresAt" in response_data


# ==============================================================================
# 2. FAILED LOGIN TEST (Incorrect Password)
# ==============================================================================
@pytest.mark.asyncio
async def test_login_fallido_contrasena_incorrecta(client, db_session):
    """Verifica que el sistema rechace el acceso si la contraseña no coincide."""

    # 1. ARRANGE: Registramos al usuario en la BD de pruebas
    target_username = "admin_test"
    correct_password = "password_secreta_123"
    wrong_password = "una_password_incorrecta_xyz"

    admin_mock = UsuarioAdmin(
        username=target_username,
        hashed_password=get_password_hash(correct_password)
    )
    db_session.add(admin_mock)
    db_session.commit()

    # Armamos el payload con la contraseña equivocada
    login_payload = {
        "usuario": target_username,
        "password": wrong_password
    }

    # 2. ACT: Intentamos loguearnos
    response = await client.post("/auth/login", json=login_payload)

    # 3. ASSERT: Debe devolver un 401 Unauthorized
    assert response.status_code == 401

    response_data = response.json()
    assert response_data["detail"] == "Incorrect username or password"


# ==============================================================================
# 3. FAILED LOGIN TEST (Non-existent User)
# ==============================================================================
@pytest.mark.asyncio
async def test_login_fallido_usuario_inexistente(client):
    """Verifica que el sistema rechace el acceso si el usuario no existe."""

    # 1. ARRANGE: Mandamos credenciales de un usuario inexistente
    login_payload = {
        "usuario": "non_existent_user_999",
        "password": "any_random_password"
    }

    # 2. ACT: Intentamos loguearnos
    response = await client.post("/auth/login", json=login_payload)

    # 3. ASSERT: Debe responder 401 Unauthorized
    assert response.status_code == 401

    response_data = response.json()
    assert response_data["detail"] == "Incorrect username or password"