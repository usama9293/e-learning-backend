from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.schemas.material import MaterialOut, MaterialCreate, MaterialUpdate
from app.models.material import Material, MaterialVersion
from app.models.user import User
from app.models.course import Course
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.core.cache import cache
from app.core.pagination import PaginationParams, paginate
from app.core.storage import upload_file, delete_file
from datetime import datetime

router = APIRouter()

@router.get("/materials", response_model=List[MaterialOut])
@cache(expire=300)
async def list_materials(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    course_id: Optional[int] = None,
    type: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(Material)
    
    if course_id:
        query = query.filter(Material.course_id == course_id)
    
    if type:
        query = query.filter(Material.type == type)
    
    if search:
        query = query.filter(
            (Material.title.ilike(f"%{search}%")) |
            (Material.description.ilike(f"%{search}%"))
        )
    
    return paginate(query, pagination)

@router.post("/materials", response_model=MaterialOut)
async def create_material(
    material: MaterialCreate,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can create materials")
    
    course = db.query(Course).filter(Course.id == material.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    file_url = await upload_file(file, "materials")
    
    new_material = Material(
        **material.dict(),
        file_url=file_url,
        created_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_material)
        db.commit()
        db.refresh(new_material)
        
        # Create initial version
        version = MaterialVersion(
            material_id=new_material.id,
            version_number=1,
            file_url=file_url,
            created_by=current_user.id,
            created_at=datetime.utcnow()
        )
        db.add(version)
        db.commit()
        
        return new_material
    except Exception as e:
        await delete_file(file_url)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create material")

@router.get("/materials/{material_id}", response_model=MaterialOut)
@cache(expire=300)
async def get_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

@router.put("/materials/{material_id}", response_model=MaterialOut)
async def update_material(
    material_id: int,
    material_update: MaterialUpdate,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can update materials")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    old_file_url = material.file_url
    file_url = None
    
    if file:
        file_url = await upload_file(file, "materials")
    
    for field, value in material_update.dict(exclude_unset=True).items():
        setattr(material, field, value)
    
    if file_url:
        material.file_url = file_url
    
    try:
        db.commit()
        db.refresh(material)
        
        if file_url:
            # Create new version
            latest_version = db.query(MaterialVersion).filter(
                MaterialVersion.material_id == material_id
            ).order_by(desc(MaterialVersion.version_number)).first()
            
            new_version = MaterialVersion(
                material_id=material_id,
                version_number=latest_version.version_number + 1 if latest_version else 1,
                file_url=file_url,
                created_by=current_user.id,
                created_at=datetime.utcnow()
            )
            db.add(new_version)
            db.commit()
            
            if old_file_url:
                await delete_file(old_file_url)
        
        return material
    except Exception as e:
        if file_url:
            await delete_file(file_url)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update material")

@router.get("/materials/{material_id}/versions")
@cache(expire=300)
async def get_material_versions(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can view material versions")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    versions = db.query(MaterialVersion).filter(
        MaterialVersion.material_id == material_id
    ).order_by(desc(MaterialVersion.version_number)).all()
    
    return versions

@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete materials")
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Delete all versions
    versions = db.query(MaterialVersion).filter(MaterialVersion.material_id == material_id).all()
    for version in versions:
        if version.file_url:
            await delete_file(version.file_url)
    
    try:
        db.delete(material)
        db.commit()
        return {"message": "Material deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete material") 