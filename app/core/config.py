from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fitoherb AI Routing Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # OSRM Provider
    OSRM_BASE_URL: str = "https://router.project-osrm.org"
    OSRM_TIMEOUT_SECONDS: float = 10.0
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://localhost:8080",
        "https://fitoherb.web.app",
        "https://fitoherb.firebaseapp.com",
        "https://fitoherb.com.br",
        "https://www.fitoherb.com.br",
        "*"
    ]
    
    # Fallback Headquarter: Fitoherb Lauro de Freitas - BA
    FITOHERB_HQ_LAT: float = -12.8992
    FITOHERB_HQ_LON: float = -38.3242
    FITOHERB_HQ_ADDRESS: str = "Rua Itaeté, 434 - Pitangueiras, Lauro de Freitas - BA, CEP: 42701-360"
    
    # Fixed Optimized Genetic Algorithm Hyperparameters (Regra P-103)
    GA_POPULATION_SIZE: int = 50
    GA_GENERATIONS: int = 35
    GA_MUTATION_RATE: float = 0.20
    GA_CROSSOVER_RATE: float = 0.85
    GA_ELITISM_COUNT: int = 2

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")

settings = Settings()
