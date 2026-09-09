from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import profiles, users

app = FastAPI(
    title="Academic Side Quest - API",
    description="API de Gestão de Horas Complementares do IFMS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(users.router)

@app.get("/", tags=["Healthcheck"])
def health_check():
    return {
        "status": "online",
        "mensagem": "API Academic Side Quest rodando perfeitamente!"
    }