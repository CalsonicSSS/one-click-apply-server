from fastapi import APIRouter
from app.models.suggestion_generation import SuggestionGenerationInputs, SuggestionGenerationResponse
from app.services.suggestion_generation import evalute_raw_html_content, generate_tailored_suggestions
from fastapi import Body
from app.custom_exceptions import NoneJobSiteError

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/cv-suggestions", response_model=SuggestionGenerationResponse)
async def evaluate_and_generate_suggestion(requestInputs: SuggestionGenerationInputs = Body(...)):
    """
    Evaluates if the provided HTML content is from a job posting site
    and extracts relevant job details for suggestion generation.
    """
    print("cv-suggestions endpoint reached")
    eval_result = await evalute_raw_html_content(requestInputs.raw_job_html_content)

    if eval_result.is_job_posting:
        suggestion_generated = await generate_tailored_suggestions(
            extracted_job_details=eval_result.extracted_job_details,
            resume_doc=requestInputs.resume_doc,
            supporting_docs=requestInputs.supporting_docs,
        )
        return suggestion_generated
    else:
        raise NoneJobSiteError(detail_message="Provided HTML content is not from a job posting site.")
