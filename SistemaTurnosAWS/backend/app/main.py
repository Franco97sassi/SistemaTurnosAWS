from fastapi import FastAPI

from app.database import Base, engine
from app.routers import clientes, profesionales, estados, turnos
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Turnos AWS",
    description="API simple para estudiar Cloud y DevOps con AWS",
    version="1.0.0"
)

app.include_router(clientes.router)
app.include_router(profesionales.router)
app.include_router(estados.router)
app.include_router(turnos.router)


@app.get("/")
def home():
    return {"mensaje": "Sistema funcionando"}