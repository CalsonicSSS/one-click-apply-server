from pydantic import BaseModel
from typing import Optional, List


class JobPostingEvalRequestInputs(BaseModel):
    website_url: Optional[str] = None
    job_posting_content: Optional[str] = None


# ------------------------------------------------


class ExtractedJobPostingDetails(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    responsibilities: List[str]
    requirements: List[str]
    location: Optional[str] = ""
    other_additional_details: Optional[str] = ""


class JobPostingEvalResultResponse(BaseModel):
    is_job_posting: bool
    extracted_job_posting_details: Optional[ExtractedJobPostingDetails] = None
