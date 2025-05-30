import os
from fastapi import UploadFile
from datetime import datetime
import aiofiles
import aiofiles.os
from typing import Optional
from pathlib import Path

# Configure upload directory
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "zip": "application/zip",
    "rar": "application/x-rar-compressed",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png"
}

async def ensure_upload_dir():
    """Ensure upload directory exists"""
    if not await aiofiles.os.path.exists(UPLOAD_DIR):
        await aiofiles.os.makedirs(UPLOAD_DIR)

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""

def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

async def upload_file(file: UploadFile, subdirectory: Optional[str] = None) -> str:
    """
    Upload a file to the server
    Returns the file path relative to the upload directory
    """
    if not is_allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}")

    await ensure_upload_dir()
    
    # Create subdirectory if specified
    if subdirectory:
        upload_path = UPLOAD_DIR / subdirectory
        if not await aiofiles.os.path.exists(upload_path):
            await aiofiles.os.makedirs(upload_path)
    else:
        upload_path = UPLOAD_DIR

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = get_file_extension(file.filename)
    filename = f"{timestamp}_{file.filename}"
    file_path = upload_path / filename

    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Return relative path
    return str(file_path.relative_to(UPLOAD_DIR))

async def delete_file(file_path: str) -> bool:
    """
    Delete a file from the server
    Returns True if file was deleted, False if file didn't exist
    """
    full_path = UPLOAD_DIR / file_path
    
    if await aiofiles.os.path.exists(full_path):
        await aiofiles.os.remove(full_path)
        return True
    return False 