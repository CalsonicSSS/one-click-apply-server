from pydantic import BaseModel
from typing import Optional, List


class ExtractedContent(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    responsibilities: list[str]
    requirements: list[str]
    location: str
    other_additional_details: str


class HtmlEvalResult(BaseModel):
    is_job_posting: bool
    extracted_job_details: Optional[ExtractedContent]


# ----------------------------------------------------------


class ResumeSuggestedChanges(BaseModel):
    where: str
    suggestion: str
    reason: str


class SuggestionGenerationResponse(BaseModel):
    resume_suggestions: List[ResumeSuggestedChanges]
    cover_letter: str


# ----------------------------------------------------------


class DocumentBase64(BaseModel):
    content: str
    file_type: str
    file_category_type: str
    name: str


class SuggestionGenerationInputs(BaseModel):
    raw_job_html_content: str
    resume_doc: DocumentBase64
    supporting_docs: Optional[List[DocumentBase64]] = None
