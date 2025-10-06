from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from app.database import get_db
from app.models.material import MaterialCreate, MaterialUpdate, MaterialResponse
from app.services.material_service import MaterialService
from app.config import get_settings

router = APIRouter(prefix="/materiales", tags=["Materiales"])
settings = get_settings()

def get_material_service(db=Depends(get_db)):
    return MaterialService(db)

@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def crear_material(
    material: MaterialCreate,
    service: MaterialService = Depends(get_material_service)
):
    """Crea un nuevo material (profesor/admin)"""
    # Verificar si el curso existe
    curso_existe = await service.verificar_curso_existe(material.cursoId, settings.ms1_cursos_url)
    if not curso_existe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El curso {material.cursoId} no existe"
        )
    
    return service.crear_material(material)

@router.get("/", response_model=List[MaterialResponse])
def listar_materiales(
    curso_id: Optional[str] = Query(None, alias="cursoId"),
    tipo: Optional[str] = None,
    publicado: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: MaterialService = Depends(get_material_service)
):
    """Lista materiales con filtros opcionales"""
    return service.obtener_materiales(curso_id, tipo, publicado, skip, limit)

@router.get("/{material_id}", response_model=MaterialResponse)
def obtener_material(
    material_id: str,
    service: MaterialService = Depends(get_material_service)
):
    """Obtiene un material por ID"""
    material = service.obtener_material_por_id(material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    return material

@router.put("/{material_id}", response_model=MaterialResponse)
def actualizar_material(
    material_id: str,
    material_update: MaterialUpdate,
    service: MaterialService = Depends(get_material_service)
):
    """Actualiza un material"""
    material = service.actualizar_material(material_id, material_update)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )
    return material

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_material(
    material_id: str,
    service: MaterialService = Depends(get_material_service)
):
    """Elimina un material"""
    if not service.eliminar_material(material_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material no encontrado"
        )

@router.get("/cursos/{curso_id}/materiales", response_model=List[MaterialResponse])
async def obtener_materiales_curso(
    curso_id: str,
    estudiante_id: Optional[str] = Query(None, alias="estudianteId"),
    service: MaterialService = Depends(get_material_service)
):
    """Obtiene materiales de un curso (verifica matrícula si es necesario)"""
    materiales = service.obtener_materiales(curso_id=curso_id, publicado=True)
    
    # Filtrar por acceso
    materiales_permitidos = []
    for material in materiales:
        if material.acceso == "publico":
            materiales_permitidos.append(material)
        elif material.acceso == "inscritos" and estudiante_id:
            # Verificar matrícula
            esta_matriculado = await service.verificar_estudiante_matriculado(
                estudiante_id, curso_id, settings.ms2_estudiantes_url
            )
            if esta_matriculado:
                materiales_permitidos.append(material)
    
    return materiales_permitidos

@router.get("/cursos/{curso_id}/count")
def contar_materiales_curso(
    curso_id: str,
    service: MaterialService = Depends(get_material_service)
):
    """Cuenta materiales de un curso"""
    count = service.contar_materiales(curso_id)
    return {"cursoId": curso_id, "totalMateriales": count}