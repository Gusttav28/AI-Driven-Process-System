from fastapi import HTTPException, UploadFile
from typing import Set
import magic

""" 
Class FileValidator, with this clases we're gonna be able to validate
the file that the user is giving us.

Three different functions that has the class to we can be aable to validate:
File Size -> No more than 10 mb, can be change in any moment.
Extensions -> Just the ones that the system would use for the moment, than wee can add more.
Content type -> Making sure that the content type is related to extention of the file, if no, we're no gonna let in. 
"""
class FileValidator:
    
    # Constructure of the class, all the paramters that needs the class to work
    def __init__(
        self, 
        max_size: int = 10 * 1024 * 1024, # 10MB
        allowed_extensions:Set[str] = None,
        allowed_content_types:Set[str] = None
    ):
        
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or {".jpg", ".png", ".jpeg", ".pdf", ".docx", ".xlsx", ".csv"}
        self.allowed_content_types = allowed_content_types or {
            "image/jpeg",
            "image/png",
            "image/jpg",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/csv",
            "text/plain",
            "application/csv"
        }
        
    """ 
    Constructure function Validate, need it to be able to declare the other functions.
    Working as entry point of the system to be able to check how's the follow of the file
    that have been upload is going.
    
    """
    async def validate(self, file:UploadFile) -> None:
        await self._validate_extension(file)
        await self._validate_size(file)
        await self._validate_content_type(file)
        
    
    
    async def _validate_extension(self, file:UploadFile) -> None:
        
        # formatting the extention to make sure what is the extention that we're locking for.
        
        exit = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        
        if exit not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File extension {exit} not allowed, Allowed: {self.allowed_extensions}"
            )
        
        return { 
            "status_code":200,
            "detail":"File size | Validation Successfully"
        }
    
    async def _validate_size(self, file: UploadFile) -> None:
        
        # Conting the size of the file as far as the systems is reading the file.
        
        file_size = 0
        while True:
            content = await file.read(1024 * 1024)
            if not content:
                break
            file_size += len(content)
            if file_size > self.max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"This file has a size of: {file.size} which is not supported by the system. Make sure that you is not grater than {self.max_size}"
                )
            
        
        # reseting the file position so it can be able to be read agai for saving.
        await file.seek(0)
        return { 
            "status_code":200,
            "detail":"File size | Validation Successfully"
        }
        
    async def _validate_content_type(self, file: UploadFile) -> None:

        """ 
            Validating actual file content type using libmagic.
            This detects the real file type by reading the file's magic bytes,
            preventing attacks where someone renames a malicious file to .jpg
        """
        
        # Reading the first 2028 bytess - enough for magic number detection.
        header = await file.read(2048)
        
        await file.seek(0) # Always reseting it to clean the memory and to read it later if need it.
        
        # Detecting the actual content type from the file header.
        detected_type = magic.from_buffer(header, mime=True)
        
        if detected_type not in self.allowed_content_types:
            raise HTTPException(
                status_code=400,
                detail=f"The content of the file: {detected_type} is not allowed by the system. Check contents allowed: {self.allowed_content_types}"
            )
            
        return { 
            "status_code":200,
            "detail":"File size | Validation Successfully"
        }