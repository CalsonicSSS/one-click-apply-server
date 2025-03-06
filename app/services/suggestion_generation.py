import json

from app.models.job_posting_eval import JobPostingEvalResultResponse, ExtractedJobPostingDetails
from app.models.resume_suggestions import ResumeSuggestionsResponse, ResumeSuggestion
from app.models.cover_letter import CoverLetterGenerationResponse
from app.models.uploaded_doc import UploadedDocument
from app.custom_exceptions import NoneJobSiteError

from app.utils.claude_handler.claude_prompts import (
    html_eval_system_prompt,
    html_eval_user_prompt_generator,
    cover_letter_gen_system_prompt,
    cover_letter_gen_user_prompt,
    resume_suggestion_gen_system_prompt,
    resume_suggestion_gen_user_prompt,
)
from app.utils.claude_handler.claude_config_apis import claude_message_api
from app.utils.claude_handler.claude_document_handler import prepare_document_for_claude
from app.custom_exceptions import GeneralServerError
from app.constants import TARGET_LLM_MODEL


async def evaluate_job_posting_html_content_handler(raw_html_content: str) -> JobPostingEvalResultResponse:
    print("evaluate_job_posting_html_content_handler runs")
    print("target llm:", TARGET_LLM_MODEL)

    system_prompt = html_eval_system_prompt
    user_prompt = html_eval_user_prompt_generator(raw_html_content)

    try:
        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL,
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            temp=0,
            max_tokens=4000,
        )

        # based on the prompt, this will return a response in JSON format
        llm_response_text_json = llm_response.content[0].text

        # to convert the JSON string to a actual Python dictionary
        response_dict = json.loads(llm_response_text_json, strict=False)

        if response_dict["is_job_posting"]:
            return JobPostingEvalResultResponse(
                is_job_posting=response_dict["is_job_posting"],
                extracted_job_posting_details=ExtractedJobPostingDetails(
                    job_title=response_dict["extracted_job_details"]["job_title"],
                    company_name=response_dict["extracted_job_details"]["company_name"],
                    job_description=response_dict["extracted_job_details"]["job_description"],
                    responsibilities=response_dict["extracted_job_details"]["responsibilities"],
                    requirements=response_dict["extracted_job_details"]["requirements"],
                    location=response_dict["extracted_job_details"]["location"],
                    other_additional_details=response_dict["extracted_job_details"]["other_additional_details"],
                ),
            )
        else:
            raise NoneJobSiteError(
                detail_message="This page doesn't appear to be a job posting. Please navigate to a single target job posting detail page."
            )

    except Exception as e:
        print(f"Error occur when evalute job posting content: {str(e)}")
        raise GeneralServerError(error_detail_message="Something went wrong while analyzing the current job posting site")


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_resume_suggestions_handler(
    extracted_job_posting_details: ExtractedJobPostingDetails, resume_doc: UploadedDocument
) -> ResumeSuggestionsResponse:
    print("generate_resume_suggestions_handler runs")
    print("target llm:", TARGET_LLM_MODEL)

    # Prepare job details text
    extracted_job_posting_details_text = f"""
    Job Title: {extracted_job_posting_details.job_title}
    Company name: {extracted_job_posting_details.company_name}
    Location: {extracted_job_posting_details.location}
    
    Job Description:
    {extracted_job_posting_details.job_description}
    
    Responsibilities:
    {extracted_job_posting_details.responsibilities}
    
    Requirements:
    {extracted_job_posting_details.requirements}
    
    Other additional Details:
    {extracted_job_posting_details.other_additional_details}
    """

    system_prompt = resume_suggestion_gen_system_prompt

    # user prompt content blocks
    # add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "my base resume"},
        prepare_document_for_claude(resume_doc),  # Handle resume with proper file type
    ]

    # add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details:"})
    user_prompt_content_blocks.append({"type": "text", "text": f"{extracted_job_posting_details_text}"})

    # add user instruction
    user_prompt_content_blocks.append({"type": "text", "text": resume_suggestion_gen_user_prompt})

    try:

        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL,
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # based on the prompt, this will return a response in JSON format
        llm_response_text_json = llm_response.content[0].text
        response_dict = json.loads(llm_response_text_json, strict=False)

        resume_suggestions = [
            ResumeSuggestion(where=sugg.get("where", ""), suggestion=sugg.get("suggestion", ""), reason=sugg.get("reason", ""))
            for sugg in response_dict.get("resume_suggestions", [])
        ]

        return ResumeSuggestionsResponse(
            resume_suggestions=resume_suggestions,
        )

    except Exception as e:
        print(f"Error occurred when generating resume suggestions: {str(e)}")
        raise GeneralServerError(error_detail_message="Something went wrong while generating resume suggestions for you")


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_cover_letter_handler(
    extracted_job_posting_details: ExtractedJobPostingDetails, resume_doc: UploadedDocument, supporting_docs: list[UploadedDocument] = None
) -> CoverLetterGenerationResponse:
    print("generate_cover_letter_handler runs")
    print("target llm:", TARGET_LLM_MODEL)

    # Prepare job details text
    extracted_job_posting_details_text = f"""
    Job Title: {extracted_job_posting_details.job_title}
    Company name: {extracted_job_posting_details.company_name}
    Location: {extracted_job_posting_details.location}
    
    Job Description:
    {extracted_job_posting_details.job_description}
    
    Responsibilities:
    {extracted_job_posting_details.responsibilities}
    
    Requirements:
    {extracted_job_posting_details.requirements}
    
    Other additional Details:
    {extracted_job_posting_details.other_additional_details}
    """

    system_prompt = cover_letter_gen_system_prompt

    # Prepare user prompt content blocks
    # add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "my base resume"},
        prepare_document_for_claude(resume_doc),
        {"type": "text", "text": "my additional professional context (if provided)"},
    ]

    # add other supporting docs
    if supporting_docs:
        for doc in supporting_docs:
            user_prompt_content_blocks.append(prepare_document_for_claude(doc))

    # add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details:"})
    user_prompt_content_blocks.append({"type": "text", "text": f"{extracted_job_posting_details_text}"})

    # add user instruction
    user_prompt_content_blocks.append({"type": "text", "text": cover_letter_gen_user_prompt})

    try:

        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL,
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # based on the prompt, this will return a response in JSON format
        llm_response_text_json = llm_response.content[0].text
        response_dict = json.loads(llm_response_text_json, strict=False)

        cover_letter = response_dict.get("cover_letter", "")
        applicant_name = response_dict.get("applicant_name", "")

        return CoverLetterGenerationResponse(
            cover_letter=cover_letter,
            company_name=extracted_job_posting_details.company_name,
            job_title_name=extracted_job_posting_details.job_title,
            location=extracted_job_posting_details.location,
            applicant_name=applicant_name,
        )

    except Exception as e:
        print(f"Error occurred when generating cover letter: {str(e)}")
        raise GeneralServerError(error_detail_message="Something went wrong while generating cover letter for you")
