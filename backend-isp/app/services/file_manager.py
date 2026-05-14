import os
import uuid
from fastapi import UploadFile, HTTPException

# Configuration
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit for QA standards

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def validate_and_save_file(file: UploadFile, folder_name: str) -> str:
    # 1. Validate Extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension {file_ext} not allowed. Use PDF, JPG, or PNG."
        )

    # 2. Generate a secure, unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. Save the file to disk
    try:
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            # QA Check: Size validation
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="File too large")
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not save file")

    return file_path