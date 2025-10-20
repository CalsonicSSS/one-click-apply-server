from pydantic import BaseModel


class UploadedDocument(BaseModel):
    base64_content: str  # this is base64 encoded string of file doc
    file_type: str  # only now is application/pdf
    name: str
