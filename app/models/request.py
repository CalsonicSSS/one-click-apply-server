from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentBase64(BaseModel):
    content: str
    file_type: str
    name: str


class GenerationRequest(BaseModel):
    job_html_content: str
    resume_doc: DocumentBase64
    supporting_docs: Optional[List[DocumentBase64]] = None
