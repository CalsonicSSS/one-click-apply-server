import anthropic
import json
from app.config import get_settings
from app.models.suggestion_generation import ResumeSuggestedChanges, SuggestionGenerationResponse, HtmlEvalResult, DocumentBase64
from app.utils.claude_api import (
    html_eval_system_prompt,
    html_eval_user_prompt_generator,
    suggestion_generation_system_prompt,
    suggestion_generation_user_prompt,
)

settings = get_settings()
client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)


def evalute_raw_html_content(raw_html_content: str) -> HtmlEvalResult:
    """
    Detects if the HTML content is from a job posting page and extracts
    relevant job details if it is.

    Args:
        raw_html_content: The original raw HTML content of the page

    Returns:
        A dictionary with:
        - is_job_posting: Boolean indicating if page is a job posting
        - reason: Explanation for the decision
        - extracted_content: Job details if is_job_posting is True
    """

    system_prompt = html_eval_system_prompt

    user_prompt = html_eval_user_prompt_generator(raw_html_content)

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            temperature=0,
            # specifies the maximum number of tokens that the model will generate in its response. It does not include the tokens from the input message
            max_tokens=4000,
        )

        # Extract JSON from response
        response_text = response.content[0].text
        # to convert the JSON string to a actual Python dictionary
        result_dict = json.loads(response_text)
        result = HtmlEvalResult(
            is_job_posting=result_dict.get("is_job_posting", False), extracted_job_details=result_dict.get("extracted_job_details", None)
        )

        return result

    except Exception as e:
        print(f"Error in job posting detection: {str(e)}")
        return HtmlEvalResult(is_job_posting=False, extracted_content=None)


# ------------------------------------------------------------------------------------------------------------------------------


def generate_tailored_suggestions(
    extracted_job_details: dict, resume_doc: DocumentBase64, supporting_docs: list[DocumentBase64] = None
) -> SuggestionGenerationResponse:
    """
    Generates tailored resume suggestions and cover letter based on the job details
    and user's documents.

    Args:
        extracted_job_details: Extracted job posting details
        resume_doc: User's resume document (base64 encoded)
        supporting_docs: User's additional supporting documents (base64 encoded)

    Returns:
        SuggestionGenerationResponse with resume suggestions and cover letter
    """

    # Prepare job details text
    extracted_job_details_text = f"""
    Job Title: {extracted_job_details.get('job_title', 'N/A')}
    Company: {extracted_job_details.get('company_name', 'N/A')}
    Location: {extracted_job_details.get('location', 'N/A')}
    
    Job Description:
    {extracted_job_details.get('job_description', 'N/A')}
    
    Responsibilities:
    {extracted_job_details.get('responsibilities', 'N/A')}
    
    Requirements:
    {extracted_job_details.get('requirements', 'N/A')}
    
    Additional Details:
    {extracted_job_details.get('additional_details', 'N/A')}
    """

    system_prompt = suggestion_generation_system_prompt

    # Prepare user prompt content blocks
    user_prompt_content_blocks = [
        {"type": "text", "text": "base resume"},
        {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": resume_doc.content},
        },
        {"type": "text", "text": "other user supporting documents if available"},
    ]

    if supporting_docs:
        for doc in supporting_docs:
            user_prompt_content_blocks.append({"type": "document", "source": {"type": "base64", "media_type": doc.file_type, "data": doc.content}})

    user_prompt_content_blocks.append({"type": "text", "text": "job posting details"})
    user_prompt_content_blocks.append({"type": "text", "text": f"Job Posting Details:\n{extracted_job_details_text}"})

    # Final user instruction
    user_prompt_content_blocks.append({"type": "text", "text": suggestion_generation_user_prompt})

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temperature=0.3,
            max_tokens=4000,
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Find JSON data in the response (handling potential text before/after JSON)
        import re

        json_match = re.search(r"({[\s\S]*})", response_text)
        if json_match:
            result = json.loads(json_match.group(1))

            # Construct SuggestionGenerationResponse
            resume_suggestions = [
                ResumeSuggestedChanges(where=sugg.get("where", ""), suggestion=sugg.get("suggestion", ""), reason=sugg.get("reason", ""))
                for sugg in result.get("resume_suggestions", [])
            ]

            return SuggestionGenerationResponse(resume_suggestions=resume_suggestions, cover_letter=result.get("cover_letter", ""))
        else:
            # Fallback if JSON parsing fails
            print("Failed to parse JSON from response")
            return SuggestionGenerationResponse(resume_suggestions=[], cover_letter="Error: Could not generate cover letter. Please try again.")

    except Exception as e:
        print(f"Error generating suggestions: {str(e)}")
        # Return fallback response
        return SuggestionGenerationResponse(resume_suggestions=[], cover_letter=f"Error generating suggestions: {str(e)}")
