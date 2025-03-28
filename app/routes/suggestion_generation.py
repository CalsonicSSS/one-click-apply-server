from fastapi import APIRouter, HTTPException
from app.custom_exceptions import NotEnoughCreditsError
from app.models.job_posting_eval import JobPostingEvalRequestInputs, JobPostingEvalResultResponse
from app.models.resume_suggestions import ResumeSuggestionGenerationRequestInputs, ResumeSuggestionsResponse
from app.models.cover_letter import CoverLetterGenerationRequestInputs, CoverLetterGenerationResponse
from app.services.suggestion_generation import (
    evaluate_job_posting_html_content_handler,
    generate_resume_suggestions_handler,
    generate_cover_letter_handler,
)
from fastapi import Body
from app.models.application_question import ApplicationQuestionAnswerRequestInputs, ApplicationQuestionAnswerResponse
from app.services.suggestion_generation import generate_application_question_answer_handler
from app.db.database import consume_credit

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/job-posting/evaluate", response_model=JobPostingEvalResultResponse)
async def evaluate_job_posting_html_content(
    requestInputs: JobPostingEvalRequestInputs = Body(...),
):
    print("/job-posting/evaluate endpoint reached")
    # Consume credit before processing
    if not await consume_credit(requestInputs.browser_id):
        raise NotEnoughCreditsError(
            error_detail_message="Not enough credits. Please purchase more."
        )
    result = await evaluate_job_posting_html_content_handler(
        raw_html_content=requestInputs.raw_job_html_content
    )
    return result


@router.post("/resume/suggestions-generate", response_model=ResumeSuggestionsResponse)
async def generate_resume_suggestions(
    requestInputs: ResumeSuggestionGenerationRequestInputs = Body(...),
):
    print("/resume/suggestions-generate endpoint reached")
    result = await generate_resume_suggestions_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc
    )
    return result


@router.post("/cover-letter/generate", response_model=CoverLetterGenerationResponse)
async def generate_cover_letter(
    requestInputs: CoverLetterGenerationRequestInputs = Body(...),
):
    print("/cover-letter/generate endpoint reached")
    result = await generate_cover_letter_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc
    )
    return result


@router.post("/application-question/answer", response_model=ApplicationQuestionAnswerResponse)
async def generate_application_question_answer(
    requestInputs: ApplicationQuestionAnswerRequestInputs = Body(...),
):
    print("/application-question/answer endpoint reached")
    result = await generate_application_question_answer_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc,
        question=requestInputs.question,
        additional_requirements=requestInputs.additional_requirements,
        supporting_docs=requestInputs.supporting_docs,
    )
    return result
