from pydantic import BaseModel


class UploadedDocument(BaseModel):
    base64_content: str  # this is base64 encoded string of file doc
    file_type: str  # either application/pdf, plain/text, or application/vnd.openxmlformats-officedocument.wordprocessingml.document
    name: str
