from fastapi import FastAPI
from app.routes import clients, auth, admin
from app.internal.database import engine
from app.internal import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ISP Procedure Management API",
    description="Optimized system for internet service self-management (Activation/Deactivation).",
    version="1.3.0"
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(clients.router)

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "message": "ISP Conectar API is operational"
    }