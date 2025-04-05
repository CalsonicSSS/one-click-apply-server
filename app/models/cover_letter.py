from pydantic import BaseModel
from typing import Optional, List
from app.models.job_posting_eval import ExtractedJobPostingDetails
from app.models.uploaded_doc import UploadedDocument


class CoverLetterGenerationRequestInputs(BaseModel):
    extracted_job_posting_details: ExtractedJobPostingDetails
    resume_doc: UploadedDocument
    # Use "= None" when you want it to be optional with a default None value.
    # Don't use "= None (other value)" if you want it to always be explicitly set a value when instanitate.
    supporting_docs: Optional[List[UploadedDocument]] = None


# ----------------------------------------------------------


class CoverLetterGenerationResponse(BaseModel):
    company_name: str
    job_title_name: str
    applicant_name: str
    cover_letter: str
    location: Optional[str] = ""
