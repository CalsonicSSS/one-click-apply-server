from pydantic import BaseModel
from typing import Optional, List


class JobExtractedContentDetails(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    responsibilities: List[str]
    requirements: List[str]
    location: str
    other_additional_details: str


class HtmlEvalResult(BaseModel):
    is_job_posting: bool
    extracted_job_details: Optional[JobExtractedContentDetails] = None


# ----------------------------------------------------------


class UploadedDocument(BaseModel):
    base64_content: str
    file_type: str
    name: str


class SuggestionGenerationInputs(BaseModel):
    raw_job_html_content: str
    resume_doc: UploadedDocument
    supporting_docs: Optional[List[UploadedDocument]] = None


# ----------------------------------------------------------


class ResumeSuggestedChanges(BaseModel):
    where: str
    suggestion: str
    reason: str


class SuggestionGenerationResponse(BaseModel):
    resume_suggestions: List[ResumeSuggestedChanges]
    cover_letter: str
