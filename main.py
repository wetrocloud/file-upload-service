from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from typing import List
import boto3
import os
import random
import datetime

app = FastAPI()

# AWS S3 Configuration
S3_BUCKET_NAME = "wetro"

# Allowed file types
ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx", "docx", "doc", "epub", "hwp", "ipynb", "jpeg", "jpg", "mbox", "md", "mp3", "mp4", "pdf", "png", "ppt", "pptm", "pptx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# Initialize S3 client
s3_client = boto3.client("s3")

def generate_file_name(original_name: str) -> str:
    """Generates a URL-friendly file name with date and random number."""
    base_name, ext = os.path.splitext(original_name)
    base_name = base_name.replace(" ", "_")
    date_str = datetime.datetime.now().strftime("%d_%m_%y")
    random_suffix = str(random.randint(100000, 999999))
    return f"{base_name}_{date_str}_{random_suffix}{ext}"

@app.post("/upload/")
async def upload_file(collection_id: str = Form(...), file: UploadFile = File(...)):
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
    
    # Generate formatted file name
    new_file_name = generate_file_name(file.filename)
    s3_path = f"{collection_id}/{new_file_name}"
    
    # Upload to S3
    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, s3_path)
        file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_path}"
        return {"filename": file.filename, "url": file_url, "message": "File uploaded successfully", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
