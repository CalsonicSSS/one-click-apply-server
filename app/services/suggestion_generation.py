import json
from app.models.suggestion_generation import (
    ResumeSuggestedChanges,
    SuggestionGenerationResponse,
    HtmlEvalResult,
    UploadedDocument,
    JobExtractedContentDetails,
)
from app.utils.claude_handler.claude_prompts import (
    html_eval_system_prompt,
    html_eval_user_prompt_generator,
    suggestion_generation_system_prompt,
    suggestion_generation_user_prompt,
)
from app.utils.claude_handler.claude_config_apis import claude_message_api
from app.utils.claude_handler.claude_document_handler import prepare_document_for_claude


async def evalute_raw_html_content(raw_html_content: str) -> HtmlEvalResult:
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
    print("evalute_raw_html_content runs")

    system_prompt = html_eval_system_prompt

    user_prompt = html_eval_user_prompt_generator(raw_html_content)

    try:
        response = await claude_message_api(
            model="claude-3-5-haiku-20241022",
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            temp=0,
            max_tokens=4000,
        )

        # based on the prompt, this will return a response in JSON format
        response_text_json = response.content[0].text

        print("---------------------------------------------------------------------------------------------------------")
        print("eval_result_dict: ", response_text_json)

        # to convert the JSON string to a actual Python dictionary
        result_dict = json.loads(response_text_json)

        if result_dict["is_job_posting"]:
            return HtmlEvalResult(
                is_job_posting=result_dict["is_job_posting"],
                extracted_job_details=JobExtractedContentDetails(
                    job_title=result_dict["extracted_job_details"]["job_title"],
                    company_name=result_dict["extracted_job_details"]["company_name"],
                    job_description=result_dict["extracted_job_details"]["job_description"],
                    responsibilities=result_dict["extracted_job_details"]["responsibilities"],
                    requirements=result_dict["extracted_job_details"]["requirements"],
                    location=result_dict["extracted_job_details"]["location"],
                    other_additional_details=result_dict["extracted_job_details"]["other_additional_details"],
                ),
            )
        else:
            return HtmlEvalResult(is_job_posting=False, extracted_job_details=None)

    except Exception as e:
        print(f"Error in job posting detection: {str(e)}")
        return HtmlEvalResult(is_job_posting=False, extracted_job_details=None)


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_tailored_suggestions(
    extracted_job_details: JobExtractedContentDetails, resume_doc: UploadedDocument, supporting_docs: list[UploadedDocument] = None
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

    print("generate_tailored_suggestions runs")

    # Prepare job details text
    extracted_job_details_text = f"""
    Job Title: {extracted_job_details.job_title}
    Company name: {extracted_job_details.company_name}
    Location: {extracted_job_details.location}
    
    Job Description:
    {extracted_job_details.job_description}
    
    Responsibilities:
    {extracted_job_details.responsibilities}
    
    Requirements:
    {extracted_job_details.requirements}
    
    Other additional Details:
    {extracted_job_details.other_additional_details}
    """

    system_prompt = suggestion_generation_system_prompt

    # Prepare user prompt content blocks
    # add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "base resume"},
        prepare_document_for_claude(resume_doc),  # Handle resume with proper file type
        {"type": "text", "text": "other user supporting document(s) if provided"},
    ]

    # add other supporting docs
    if supporting_docs:
        for doc in supporting_docs:
            user_prompt_content_blocks.append(prepare_document_for_claude(doc))

    # add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details"})
    user_prompt_content_blocks.append({"type": "text", "text": f"Job Posting Details:\n{extracted_job_details_text}"})

    # add user instruction
    user_prompt_content_blocks.append({"type": "text", "text": suggestion_generation_user_prompt})

    try:

        response = await claude_message_api(
            model="claude-3-5-haiku-20241022",
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # based on the prompt, this will return a response in JSON format
        response_text_json = response.content[0].text
        response_dict = json.loads(response_text_json)

        resume_suggestions = [
            ResumeSuggestedChanges(where=sugg.get("where", ""), suggestion=sugg.get("suggestion", ""), reason=sugg.get("reason", ""))
            for sugg in response_dict.get("resume_suggestions", [])
        ]

        cover_letter = response_dict.get("cover_letter", "")

        return SuggestionGenerationResponse(resume_suggestions=resume_suggestions, cover_letter=cover_letter)

    except Exception as e:
        print(f"Error generating suggestions: {str(e)}")
        # Return fallback response
        return SuggestionGenerationResponse(resume_suggestions=[], cover_letter=f" ")
