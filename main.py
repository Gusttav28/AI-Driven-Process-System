from fastapi import FastAPI, UploadFile, HTTPException, File
import aiofiles
from pathlib import Path
from processing_files.validators import FileValidator
from processing_files.processing_security.file_security import generate_safe_filename

app = FastAPI()

# Create upload directory if doesn't exist

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Configuring validator for file uploads

image_validador = FileValidator(
    max_size= 5 * 1024 * 1024, # 5mb
    allowed_extensions={".jpg", ".png", ".jpeg"},
    allowed_content_types={"image/jpeg", "image/png", "image/jpg",}
) 

file_validator = FileValidator(
    max_size= 20 * 1024 * 1024, # 20mb
    allowed_extensions={".pdf", ".docx", ".xlsx", ".csv"},
    allowed_content_types={ 
            "application/pdf", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/csv",
            "text/plain",
            "application/csv"
        }
)

@app.post("/upload/images")
async def upload_images(file: UploadFile = File(...)):
    await image_validador.validate(file)
    
    safe_filename = await generate_safe_filename(file.filename)
    file_path = UPLOAD_DIR / safe_filename

     # Using aiofiles for async file writting - important for performance
    # when handling multiple concurrent uploads
    async with aiofiles.open(file_path, "wb") as f:
        try:
            # Reading and Writing the file in a "chunck way" to handle large files efficiantly
            # Without loading the entire file into memory 
            while True:
                # Peace by peace we're reading the file and writing it
                content = await file.read(1024 * 1024)
                # when there's not content the "Chunck" would stop
                if not content:
                    break
                
                await f.write(content)    
        except ValueError:
            raise HTTPException(
                status_code= 400,
                detail="Something went wrong"
            )
            
    return {
        "message":"upload successfully",
        "file_name":file.filename,
        "file_size": file.size,
        "content_type":file.content_type
    }
        
        

@app.get("/")
async def main():
    return {"message":"working"}


# uploading the file here --->
    
@app.post("/upload/files")
async def upload_files(file: UploadFile = File(...)):
    await file_validator.validate(file)
    
    safe_filename = await generate_safe_filename(file.filename)
    
    # buildinng the file path where we save the file
    file_path = UPLOAD_DIR / safe_filename
    
    # Using aiofiles for async file writting - important for performance
    # when handling multiple concurrent uploads
    async with aiofiles.open(file_path, "wb") as f:
        # Reading and Writing the file in a "chunck way" to handle large files efficiantly
        # Without loading the entire file into memory 
        try:
            while True:
                # Peace by peace we're reading the file and writing it
                content = await file.read(1024 * 1024)
                # If there's not content the "Chunck" stop
                if not content:
                    break
                await f.write(content)    
        
        except ValueError:
            raise HTTPException(
                status_code= 400,
                detail="Something went wrong"
            )
        
    # file_size = os.path.getsize(file_path)
            
    # Json retrive informations
    return {
        "message":"upload successfully",
        "file_name":file.filename,
        "file_size": file.size,
        "content_type":file.content_type
    }
