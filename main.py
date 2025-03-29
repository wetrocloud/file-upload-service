from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import os

app = FastAPI()

# Allowed file types
ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx", "docx", "doc", "epub", "hwp", "ipynb", "jpeg", "jpg", "mbox", "md", "mp3", "mp4", "pdf", "png", "ppt", "pptm", "pptx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    # Check file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{file_extension}")
    
    # Reset file pointer after reading
    await file.seek(0)
    
    return {"filename": file.filename, "content_type": file.content_type, "message": "File uploaded successfully"}
