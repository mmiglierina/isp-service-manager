# app/internal/mock_db.py

# Esta lista actuará como nuestra "Base de Datos" temporal
TRAMITES_STORAGE = [
    {
        "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "dni": "12345678",
        "type": "ALTA",
        "status": "en_curso",
        "created_at": "2024-05-21T10:00:00",
        "nombre": "Juan",
        "apellido": "Perez",
        "email": "juan@example.com",
        "archivos": ["uploads/dni.pdf", "uploads/impuesto.pdf"]
    }
]

def add_tramite(data: dict):
    TRAMITES_STORAGE.append(data)

def get_all():
    return TRAMITES_STORAGE

def update_status(uuid: str, new_status: str):
    for t in TRAMITES_STORAGE:
        if t["uuid"] == uuid:
            t["status"] = new_status
            return True
    return False