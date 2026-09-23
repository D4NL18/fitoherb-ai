from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routers.routing_router import router as routing_router
from app.api.v1.routers.health_router import router as health_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Microserviço de Inteligência Artificial para Otimização de Rotas Comerciais da Fitoherb Nordeste.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir requisições do frontend Angular e backend Spring Boot
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rotas da API v1
app.include_router(health_router, prefix="/api/v1")
app.include_router(health_router) # /health na raiz para probes do Cloud Run
app.include_router(routing_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Fitoherb AI Routing Service Online",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
