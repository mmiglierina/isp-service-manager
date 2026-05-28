# scripts/seed.py
import sys
import os
import getpass

# encuentre la carpeta 'app' sin importar desde dónde se ejecute el script.
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

from app.internal.database import SessionLocal, engine
from app.internal import models
from app.services.auth import get_password_hash

def crear_administrador_interactivo():
    print("\n=============================================")
    print("   GENERADOR INTERACTIVO DE ADMINISTRADORES  ")
    print("=============================================\n")

    username = input("Defina el usuario administrador: ").strip()
    if not username:
        print("Error: El usuario no puede estar vacío.")
        return

    password = getpass.getpass("Defina la contraseña: ")
    confirm = getpass.getpass("Confirme la contraseña: ")

    if password != confirm:
        print("Error: Las contraseñas no coinciden.")
        return

    db = SessionLocal()
    try:
        # Verificar si ya existe en la tabla de Postgres
        existe = db.query(models.UsuarioAdmin).filter(models.UsuarioAdmin.username == username).first()
        if existe:
            print(f"Error: El administrador '{username}' ya existe.")
            return

        # Hasheamos con Argon2/Bcrypt usando tu service/auth.py
        hashed = get_password_hash(password)

        nuevo_admin = models.UsuarioAdmin(username=username, hashed_password=hashed)
        db.add(nuevo_admin)
        db.commit()
        print(f"\n[ÉXITO] El administrador '{username}' fue insertado en PostgreSQL.")

    except Exception as e:
        print(f"Error al conectar con PostgreSQL en Docker: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Asegura la existencia de la tabla antes de sembrar
    models.Base.metadata.create_all(bind=engine)
    crear_administrador_interactivo()