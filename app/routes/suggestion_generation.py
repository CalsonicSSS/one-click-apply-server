from fastapi import APIRouter, HTTPException
from app.models.suggestion_generation import SuggestionGenerationInputs, SuggestionGenerationResponse
from app.services.suggestion_generation import evalute_raw_html_content, generate_tailored_suggestions

# Tags are used to group related endpoints in the automatically generated API documentation (Swagger UI or ReDoc).
router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/cv-suggestions", response_model=SuggestionGenerationResponse)
async def evaluate_and_generate_suggestion(request: SuggestionGenerationInputs):
    """
    Evaluates if the provided HTML content is from a job posting site
    and extracts relevant job details for suggestion generation.
    """
    eval_result = evalute_raw_html_content(request.raw_job_html_content)

    if eval_result.is_job_posting:
        suggestion_generated = generate_tailored_suggestions(
            extracted_job_details=eval_result.extracted_job_details, resume_doc=request.resume_doc, supporting_docs=request.supporting_docs
        )
        return suggestion_generated
    else:
        print("Provided HTML content is not from a job posting site.")
        raise HTTPException(status_code=400, detail="Provided HTML content is not from a job posting site.")
