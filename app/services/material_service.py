from pymongo.database import Database
from bson import ObjectId
from typing import List, Optional
from app.models.material import MaterialCreate, MaterialUpdate, MaterialResponse
from datetime import datetime
import logging
import httpx

logger = logging.getLogger(__name__)

class MaterialService:
    def __init__(self, db: Database):
        self.collection = db["materiales"]
        self.collection.create_index("cursoId")
        self.collection.create_index("tipo")
        self.collection.create_index("tags")
    
    async def verificar_curso_existe(self, curso_id: str, ms1_url: str) -> bool:
        """Verifica si el curso existe en MS1"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{ms1_url}/cursos/{curso_id}", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"No se pudo verificar curso en MS1: {e}")
            return True  # Permitir operación si MS1 no responde
    
    async def verificar_estudiante_matriculado(self, estudiante_id: str, curso_id: str, ms2_url: str) -> bool:
        """Verifica si el estudiante está matriculado en el curso"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{ms2_url}/matriculas/verificar",
                    params={"estudianteId": estudiante_id, "cursoId": curso_id},
                    timeout=5.0
                )
                return response.status_code == 200 and response.json().get("matriculado", False)
        except Exception as e:
            logger.warning(f"No se pudo verificar matrícula en MS2: {e}")
            return False
    
    def crear_material(self, material: MaterialCreate) -> MaterialResponse:
        """Crea un nuevo material"""
        material_dict = material.model_dump()
        material_dict["fechaCreacion"] = datetime.now()
        
        result = self.collection.insert_one(material_dict)
        material_dict["_id"] = str(result.inserted_id)
        
        return MaterialResponse(**material_dict)
    
    def obtener_material_por_id(self, material_id: str) -> Optional[MaterialResponse]:
        """Obtiene un material por su ID"""
        try:
            material = self.collection.find_one({"_id": ObjectId(material_id)})
            if material:
                material["_id"] = str(material["_id"])
                return MaterialResponse(**material)
        except Exception as e:
            logger.error(f"Error obteniendo material: {e}")
        return None
    
    def obtener_materiales(
        self,
        curso_id: Optional[str] = None,
        tipo: Optional[str] = None,
        publicado: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MaterialResponse]:
        """Obtiene materiales con filtros opcionales"""
        filtros = {}
        
        if curso_id:
            filtros["cursoId"] = curso_id
        if tipo:
            filtros["tipo"] = tipo
        if publicado is not None:
            filtros["publicado"] = publicado
        
        materiales = self.collection.find(filtros).skip(skip).limit(limit).sort("fechaCreacion", -1)
        
        result = []
        for material in materiales:
            material["_id"] = str(material["_id"])
            result.append(MaterialResponse(**material))
        
        return result
    
    def actualizar_material(self, material_id: str, material_update: MaterialUpdate) -> Optional[MaterialResponse]:
        """Actualiza un material"""
        try:
            update_data = {k: v for k, v in material_update.model_dump().items() if v is not None}
            
            if not update_data:
                return self.obtener_material_por_id(material_id)
            
            result = self.collection.find_one_and_update(
                {"_id": ObjectId(material_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                result["_id"] = str(result["_id"])
                return MaterialResponse(**result)
        except Exception as e:
            logger.error(f"Error actualizando material: {e}")
        return None
    
    def eliminar_material(self, material_id: str) -> bool:
        """Elimina un material"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(material_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error eliminando material: {e}")
            return False
    
    def contar_materiales(self, curso_id: Optional[str] = None) -> int:
        """Cuenta materiales por curso"""
        filtros = {"cursoId": curso_id} if curso_id else {}
        return self.collection.count_documents(filtros)