from fastapi import APIRouter, Depends, HTTPException,status,UploadFile
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.material import MaterialOut, MaterialCreate, MaterialUpdate
from app.models.material import Material
from app.api.api_v1.deps import get_db, get_current_user
from app.models.user import User
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import shutil
import os
import uuid
from datetime import datetime
from app.models.session import Session as SessionModel
from app.core.create_log import create_log

router = APIRouter()

@router.get("/materials", response_model=List[MaterialOut])
def list_materials(db: Session = Depends(get_db)):
    return db.query(Material).all()

@router.post("/materials", response_model=MaterialOut)
def create_material(material: MaterialCreate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    new_material = Material(**material.dict())
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    create_log(db,"Materials Created", current_user.email)
    return new_material

UPLOAD_DIR = "uploads/materials"
os.makedirs(UPLOAD_DIR,exist_ok=True)
@router.post("/materials/upload", response_model=MaterialOut)
async def upload_material(
    name: str = Form(...),
    description: str = Form(...),
    session_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can create materials")
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generate unique filename
            

    # Save file
    
    try:
        for file in files:
            ext = os.path.splitext(file.filename)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join("uploads/materials", unique_name)

            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            material = Material(session_id= session_id,
                        name= name, 
                        file_path= file_path,
                        description = description,
                        link = f"/materials/download/{unique_name}",
                        created_at=datetime.utcnow()
                         )
            db.add(material)
            db.commit()
            db.refresh(material)
            
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # download_url = f"/materials/download/{filename}"

    # Simulate saving to DB (you should replace this with your DB call)
    

    create_log(db,"Materials Created", current_user.email)
    # Return the material (simulate the DB record)
    return material

@router.get("/materials/{session_id}", response_model=list[MaterialOut])
def get_material(session_id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    material = db.query(Material).filter(Material.session_id == session_id).all()
    
        # if not material:
    #     raise HTTPException(status_code=404, detail="Material not found")
    return material

@router.put("/materials/{material_id}", response_model=MaterialOut)
def update_material(material_id: int, material_update: MaterialUpdate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    for field, value in material_update.dict(exclude_unset=True).items():
        setattr(material, field, value)
    db.commit()
    create_log(db,"Materials Updated", current_user.email)
    db.refresh(material)
    return material

@router.delete("/materials/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(material)
    create_log(db,"Materials Deleted", current_user.email)
    db.commit()
    return {"detail": "Material deleted"}


from fastapi.responses import FileResponse

@router.get("/materials/download/{filename}")
async def download_material_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')