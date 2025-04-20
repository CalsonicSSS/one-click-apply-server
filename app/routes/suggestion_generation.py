from fastapi import APIRouter
from app.models.job_posting_eval import JobPostingEvalRequestInputs, JobPostingEvalResultResponse
from app.models.resume_suggestions import (
    ResumeGenerationRequestInputs,
    ResumeSuggestionsResponse,
    FullResumeGenerationResponse,
)
from app.models.cover_letter import CoverLetterGenerationRequestInputs, CoverLetterGenerationResponse
from app.services.suggestion_generation import (
    evaluate_job_posting_content_handler,
    generate_resume_suggestions_handler,
    generate_cover_letter_handler,
    generate_application_question_answer_handler,
    generate_full_resume_handler,
)
from fastapi import Body
from app.models.application_question import ApplicationQuestionAnswerRequestInputs, ApplicationQuestionAnswerResponse
from app.utils.firecrawl import firecrawl_app
from app.custom_exceptions import FirecrawlError, NotEnoughCreditsError, GeneralServerError
from app.db.database import check_user_credits

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/job-posting/evaluate", response_model=JobPostingEvalResultResponse)
async def evaluate_job_posting_html_content(requestInputs: JobPostingEvalRequestInputs = Body(...)):
    print("/job-posting/evaluate endpoint reached")
    raw_content = None

    # Check user credits
    if not await check_user_credits(requestInputs.browser_id):
        raise NotEnoughCreditsError(error_detail_message="Not enough credits. Let's get some! Wohoo 🚀")

    if requestInputs.website_url:
        print("web url:", requestInputs.website_url)
        try:
            # Use Firecrawl to scrape the website
            scrape_result = firecrawl_app.scrape_url(requestInputs.website_url, params={"formats": ["markdown"]})
            raw_content = scrape_result.get("markdown", "").strip()

            # Validate the scraped content
            if not raw_content or len(raw_content) < 1000:
                raise FirecrawlError(error_detail_message="firecrawl error")

        except FirecrawlError:
            print("Firecrawl error: insufficient content extracted", e)
            raise

        except Exception as e:
            print("Error scraping URL using Firecrawl:", e)
            raise FirecrawlError(error_detail_message="firecrawl error")

    elif requestInputs.job_posting_content:
        raw_content = requestInputs.job_posting_content

    else:
        raise GeneralServerError(error_detail_message="No web URL nor manual content provided.")

    result = await evaluate_job_posting_content_handler(raw_content=raw_content)
    return result


@router.post("/resume-suggestions/generate", response_model=ResumeSuggestionsResponse)
async def generate_resume_suggestions(requestInputs: ResumeGenerationRequestInputs = Body(...)):
    print("/resume/suggestions-generate endpoint reached")
    result = await generate_resume_suggestions_handler(
        extracted_job_posting_details=requestInputs.extracted_job_posting_details,
        resume_doc=requestInputs.resume_doc,
        supporting_docs=requestInputs.supporting_docs,
    )
    return result


@router.post("/resume/generate", response_model=FullResumeGenerationResponse)
async def generate_full_resume(requestInputs: ResumeGenerationRequestInputs = Body(...)):
    print("/resume/generate endpoint reached")
    result = await generate_full_resume_handler(
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
        browser_id=requestInputs.browser_id,
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
