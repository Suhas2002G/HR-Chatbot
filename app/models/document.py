from pydantic import BaseModel


class DocumentChunk(BaseModel):
    chunk_id: str
    document_name: str
    source_path: str
    text: str
    section: str
