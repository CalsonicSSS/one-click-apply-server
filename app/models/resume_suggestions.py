from pydantic import BaseModel
from typing import Optional, List
from app.models.job_posting_eval import ExtractedJobPostingDetails
from app.models.uploaded_doc import UploadedDocument


class ResumeSuggestionGenerationRequestInputs(BaseModel):
    extracted_job_posting_details: ExtractedJobPostingDetails
    resume_doc: UploadedDocument
    supporting_docs: Optional[List[UploadedDocument]] = None


# ----------------------------------------------------------


class ResumeSuggestion(BaseModel):
    where: str
    suggestion: str
    reason: str


class ResumeSuggestionsResponse(BaseModel):
    resume_suggestions: List[ResumeSuggestion]
