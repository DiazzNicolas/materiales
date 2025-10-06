from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # MongoDB
    mongodb_host: str
    mongodb_port: int = 27017
    mongodb_database: str
    mongodb_user: str = ""
    mongodb_password: str = ""
    
    # Servicio
    service_port: int = 8003
    service_host: str = "0.0.0.0"
    
    # Microservicios externos
    ms1_cursos_url: str
    ms2_estudiantes_url: str
    
    # App
    app_name: str = "MS3-Contenido-Materiales"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def mongodb_url(self) -> str:
        if self.mongodb_user and self.mongodb_password:
            return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_database}"
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_database}"

@lru_cache()
def get_settings():
    return Settings()