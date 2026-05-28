import os
import sys

# FORZAMOS el cambio de variable de entorno en la memoria de ejecución antes de importar la app.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ahora sí importamos lo que requiere la base armada y la aplicación
from app.internal.database import Base, get_db
from app.main import app
from httpx import AsyncClient, ASGITransport

# Creación de mock para logueo de usuario
from app.routes.admin import get_current_user

# 3. Creamos el motor de base de datos SQLite para las pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest_asyncio.fixture(scope="function")
async def admin_client(db_session):
    """
    Cliente HTTP que mockea la autenticación de administrador saltándose el JWT.
    """
    # 1. Definimos el comportamiento mockeado de la dependencia
    def _mock_get_current_user():
        return "admin_user"  # Retorna el string que espera recibir tu endpoint

    # 2. Inyectamos los Overrides (Base de datos + Autenticación)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = _mock_get_current_user

    # 3. Creamos el cliente asíncrono
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # IMPORTANTE: FastAPI requiere que se envíe la cabecera 'Authorization',
        # de lo contrario, HTTPBearer saltará con un 403 antes de ejecutar el override.
        ac.headers.update({"Authorization": "Bearer token_simulado"})
        yield ac

    # 4. Limpiamos todo al terminar el test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos limpia en la RAM para cada función de test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Reemplaza la dependencia de la BD en FastAPI inyectando el motor de test."""

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # Aplicamos el Override para redirigir los endpoints al motor en memoria
    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()