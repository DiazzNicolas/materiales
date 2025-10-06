from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class MaterialBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    tipo: Literal["video", "documento", "quiz", "tarea"]
    recurso: str = Field(..., min_length=1)
    cursoId: str = Field(..., min_length=1)
    autor: Optional[str] = None
    tags: Optional[List[str]] = []
    publicado: bool = True
    acceso: Literal["publico", "inscritos"] = "inscritos"
    
    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Introducción a Python - Clase 1",
                "descripcion": "Primera clase del curso de Python",
                "tipo": "video",
                "recurso": "https://example.com/videos/python-clase1.mp4",
                "cursoId": "CURSO-001",
                "autor": "Prof. Juan Pérez",
                "tags": ["python", "introduccion", "fundamentos"],
                "publicado": True,
                "acceso": "inscritos"
            }
        }

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    tipo: Optional[Literal["video", "documento", "quiz", "tarea"]] = None
    recurso: Optional[str] = None
    autor: Optional[str] = None
    tags: Optional[List[str]] = None
    publicado: Optional[bool] = None
    acceso: Optional[Literal["publico", "inscritos"]] = None

class MaterialInDB(MaterialBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    fechaCreacion: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MaterialResponse(BaseModel):
    id: str = Field(..., alias="_id")
    titulo: str
    descripcion: Optional[str]
    tipo: str
    recurso: str
    cursoId: str
    autor: Optional[str]
    tags: List[str]
    publicado: bool
    acceso: str
    fechaCreacion: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}