import uuid
from pathlib import Path

async def generate_safe_filename(original: str) -> str:
    clean_name = Path(original).name
    unique_prefix = str(uuid.uuid4())[:8]
    
    return f"{unique_prefix}_{clean_name}"