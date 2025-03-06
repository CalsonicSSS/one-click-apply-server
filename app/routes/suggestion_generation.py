from fastapi import APIRouter
from app.models.job_posting_eval import JobPostingEvalRequestInputs, JobPostingEvalResultResponse
from app.models.resume_suggestions import ResumeSuggestionGenerationRequestInputs, ResumeSuggestionsResponse
from app.models.cover_letter import CoverLetterGenerationRequestInputs, CoverLetterGenerationResponse
from app.services.suggestion_generation import (
    evaluate_job_posting_html_content_handler,
    generate_resume_suggestions_handler,
    generate_cover_letter_handler,
)
from fastapi import Body

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/job-posting/evaluate", response_model=JobPostingEvalResultResponse)
async def evaluate_job_posting_html_content(requestInputs: JobPostingEvalRequestInputs = Body(...)):
    print("/job-posting/evaluate endpoint reached")
    result = await evaluate_job_posting_html_content_handler(raw_html_content=requestInputs.raw_job_html_content)
    return result


@router.post("/resume/suggestions-generate", response_model=ResumeSuggestionsResponse)
async def generate_resume_suggestions(requestInputs: ResumeSuggestionGenerationRequestInputs = Body(...)):
    print("/resume/suggestions-generate endpoint reached")
    result = await generate_resume_suggestions_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details, resume_doc=requestInputs.resume_doc
    )
    return result


@router.post("/cover-letter/generate", response_model=CoverLetterGenerationResponse)
async def generate_cover_letter(requestInputs: CoverLetterGenerationRequestInputs = Body(...)):
    print("/cover-letter/generate endpoint reached")
    result = await generate_cover_letter_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details, resume_doc=requestInputs.resume_doc
    )
    return result
