from pydantic import BaseModel
from typing import Optional, List
from app.models.job_posting_eval import ExtractedJobPostingDetails
from app.models.uploaded_doc import UploadedDocument


class ApplicationQuestionAnswerRequestInputs(BaseModel):
    extracted_job_posting_details: ExtractedJobPostingDetails
    resume_doc: UploadedDocument
    question: str
    additional_requirements: Optional[str] = None
    supporting_docs: Optional[List[UploadedDocument]] = None


class ApplicationQuestionAnswerResponse(BaseModel):
    question: str
    answer: str
