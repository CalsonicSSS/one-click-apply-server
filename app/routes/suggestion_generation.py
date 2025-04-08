from fastapi import APIRouter, HTTPException
from app.models.job_posting_eval import JobPostingEvalRequestInputs, JobPostingEvalResultResponse
from app.models.resume_suggestions import ResumeSuggestionGenerationRequestInputs, ResumeSuggestionsResponse
from app.models.cover_letter import CoverLetterGenerationRequestInputs, CoverLetterGenerationResponse
from app.services.suggestion_generation import (
    evaluate_job_posting_html_content_handler,
    generate_resume_suggestions_handler,
    generate_cover_letter_handler,
    generate_application_question_answer_handler,
)
from fastapi import Body
from app.models.application_question import ApplicationQuestionAnswerRequestInputs, ApplicationQuestionAnswerResponse
from app.utils.firecrawl import firecrawl_app

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/job-posting/evaluate", response_model=JobPostingEvalResultResponse)
async def evaluate_job_posting_html_content(requestInputs: JobPostingEvalRequestInputs = Body(...)):
    print("/job-posting/evaluate endpoint reached")
    raw_content = requestInputs.raw_job_html_content
    if requestInputs.website_url:
        # Use firecrawl to scrape the website
        scrape_result = firecrawl_app.scrape_url(requestInputs.website_url, params={'formats': ['markdown', 'html']})
        raw_content = scrape_result['markdown']
        
    result = await evaluate_job_posting_html_content_handler(raw_content=raw_content, browser_id=requestInputs.browser_id)
    return result


@router.post("/resume-suggestions/generate", response_model=ResumeSuggestionsResponse)
async def generate_resume_suggestions(requestInputs: ResumeSuggestionGenerationRequestInputs = Body(...)):
    print("/resume/suggestions-generate endpoint reached")
    result = await generate_resume_suggestions_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc,
        supporting_docs=requestInputs.supporting_docs,
    )
    return result


@router.post("/cover-letter/generate", response_model=CoverLetterGenerationResponse)
async def generate_cover_letter(requestInputs: CoverLetterGenerationRequestInputs = Body(...)):
    print("/cover-letter/generate endpoint reached")
    result = await generate_cover_letter_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc,
        supporting_docs=requestInputs.supporting_docs,
    )
    return result


@router.post("/application-question/answer", response_model=ApplicationQuestionAnswerResponse)
async def generate_application_question_answer(requestInputs: ApplicationQuestionAnswerRequestInputs = Body(...)):
    print("/application-question/answer endpoint reached")
    result = await generate_application_question_answer_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc,
        question=requestInputs.question,
        additional_requirements=requestInputs.additional_requirements,
        supporting_docs=requestInputs.supporting_docs,
    )
    return result
