from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class Database:
    client: MongoClient = None
    
    @classmethod
    def connect_db(cls):
        """Conecta a MongoDB"""
        try:
            cls.client = MongoClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000
            )
            # Verificar conexión
            cls.client.admin.command('ping')
            logger.info(f"✅ Conectado a MongoDB: {settings.mongodb_database}")
        except ConnectionFailure as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    @classmethod
    def close_db(cls):
        """Cierra la conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("🔌 Conexión a MongoDB cerrada")
    
    @classmethod
    def get_database(cls):
        """Obtiene la instancia de la base de datos"""
        if cls.client is None:
            cls.connect_db()
        return cls.client[settings.mongodb_database]

def get_db():
    """Dependency para obtener la base de datos"""
    return Database.get_database()