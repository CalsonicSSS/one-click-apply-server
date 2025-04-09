import traceback
from app.models.job_posting_eval import JobPostingEvalResultResponse, ExtractedJobPostingDetails
from app.models.resume_suggestions import ResumeSuggestionsResponse, ResumeSuggestion, FullResumeGenerationResponse, ResumeSection
from app.models.cover_letter import CoverLetterGenerationResponse
from app.models.uploaded_doc import UploadedDocument
from app.models.application_question import ApplicationQuestionAnswerResponse
from app.custom_exceptions import NoneJobSiteError, GeneralServerError, NotEnoughCreditsError, LLMResponseParsingError
from typing import Optional, List

from app.utils.claude_handler.claude_prompts import (
    job_post_evaltract_user_prompt_template,
    job_post_evaltract_system_prompt,
    cover_letter_gen_system_prompt,
    cover_letter_gen_user_prompt,
    resume_suggestion_gen_system_prompt,
    resume_suggestion_gen_user_prompt,
    application_question_system_prompt,
    application_question_user_prompt_template,
    full_resume_gen_system_prompt,
    full_resume_gen_user_prompt,
)
from app.utils.claude_handler.claude_config_apis import claude_message_api
from app.utils.claude_handler.claude_document_handler import prepare_document_for_claude
from app.constants import TARGET_LLM_MODEL_HAIKU, TARGET_LLM_MODEL_SONNET
from app.db.database import consume_credit
from app.utils.data_parsing import parse_llm_json_response


async def evaluate_job_posting_content_handler(raw_content: str, browser_id: str) -> JobPostingEvalResultResponse:
    print("evaluate_job_posting_html_content_handler runs")
    print("target llm:", TARGET_LLM_MODEL_HAIKU)

    print("raw_content:", raw_content)
    job_post_evaltract_user_prompt = job_post_evaltract_user_prompt_template.format(raw_content=raw_content)

    try:
        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL_HAIKU,
            system_prompt=job_post_evaltract_system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": job_post_evaltract_user_prompt}]}],
            temp=0,
            max_tokens=4000,
        )

        # Get the response text from Claude
        llm_response_text = llm_response.content[0].text

        # Parse the response using our utility function
        response_dict = parse_llm_json_response(llm_response_text)

        # At this point, it's safe to consume a user credit
        if not await consume_credit(browser_id):
            raise NotEnoughCreditsError(error_detail_message="Not enough credits. Please purchase more.")

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
                error_detail_message="This page doesn't appear to be a job posting. Please navigate to a single target job posting detail page."
            )
    except NoneJobSiteError:
        print(traceback.format_exc())
        print("NoneJobSiteError occurred")
        raise
    except NotEnoughCreditsError:
        print(traceback.format_exc())
        print("NotEnoughCreditsError occurred")
        raise
    except LLMResponseParsingError:
        print(traceback.format_exc())
        print("LLMResponseParsingError occurred")
        raise
    except Exception as e:
        print(f"Error occur when evalute job posting content: {str(e)}")
        raise GeneralServerError(error_detail_message="Sorry could not generate the response at this moment. Please retry later")


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_resume_suggestions_handler(
    extracted_job_posting_details: ExtractedJobPostingDetails, resume_doc: UploadedDocument, supporting_docs: list[UploadedDocument] = None
) -> ResumeSuggestionsResponse:
    print("generate_resume_suggestions_handler runs")
    print("target llm:", TARGET_LLM_MODEL_HAIKU)

    # Prepare job details text
    extracted_full_job_posting_details_text = f"""
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

    # user prompt content blocks
    # add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "my base resume"},
        prepare_document_for_claude(resume_doc),  # Handle resume with proper file type
    ]

    # add other supporting docs
    if supporting_docs:
        user_prompt_content_blocks.append({"type": "text", "text": "my additional professional context:"})
        for doc in supporting_docs:
            user_prompt_content_blocks.append(prepare_document_for_claude(doc))

    # add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details:"})
    user_prompt_content_blocks.append({"type": "text", "text": f"{extracted_full_job_posting_details_text}"})

    # add user instruction
    user_prompt_content_blocks.append({"type": "text", "text": resume_suggestion_gen_user_prompt})

    try:
        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL_HAIKU,
            system_prompt=resume_suggestion_gen_system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # Parse the response using our utility function
        llm_response_text = llm_response.content[0].text
        response_dict = parse_llm_json_response(llm_response_text)

        resume_suggestions = [
            ResumeSuggestion(where=sugg.get("where", ""), suggestion=sugg.get("suggestion", ""), reason=sugg.get("reason", ""))
            for sugg in response_dict.get("resume_suggestions", [])
        ]

        return ResumeSuggestionsResponse(
            resume_suggestions=resume_suggestions,
        )

    except LLMResponseParsingError:
        print(traceback.format_exc())
        print("LLMResponseParsingError occurred")
        raise
    except Exception as e:
        print(f"Error occur when evalute job posting content: {str(e)}")
        raise GeneralServerError(error_detail_message="Sorry could not generate the response at this moment. Please retry later")


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_full_resume_handler(
    extracted_job_posting_details: ExtractedJobPostingDetails, resume_doc: UploadedDocument, supporting_docs: list[UploadedDocument] = None
) -> FullResumeGenerationResponse:
    print("generate_full_resume_handler runs")
    print("target llm:", TARGET_LLM_MODEL_SONNET)

    # Prepare job details text
    extracted_full_job_posting_details_text = f"""
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

    # user prompt content blocks
    # add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "my base resume:"},
        prepare_document_for_claude(resume_doc),
    ]

    # add other supporting docs
    if supporting_docs:
        user_prompt_content_blocks.append({"type": "text", "text": "my additional professional context:"})
        for doc in supporting_docs:
            user_prompt_content_blocks.append(prepare_document_for_claude(doc))

    # add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details:"})
    user_prompt_content_blocks.append({"type": "text", "text": f"{extracted_full_job_posting_details_text}"})

    # add user instruction
    user_prompt_content_blocks.append({"type": "text", "text": full_resume_gen_user_prompt})
    try:
        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL_HAIKU,
            system_prompt=full_resume_gen_system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # Parse the response using our utility function
        llm_response_text = llm_response.content[0].text
        response_dict = parse_llm_json_response(llm_response_text)

        return FullResumeGenerationResponse(
            applicant_name=response_dict.get("applicant_name", ""),
            contact_info=response_dict.get("contact_info", ""),
            summary=response_dict.get("summary", []),
            skills=response_dict.get("skills", []),
            sections=[
                ResumeSection(title=section.get("title", ""), content=section.get("content", "")) for section in response_dict.get("sections", [])
            ],
            full_resume_text=response_dict.get("full_resume_text", ""),
        )

    except LLMResponseParsingError:
        print(traceback.format_exc())
        print("LLMResponseParsingError occurred")
        raise
    except Exception as e:
        print(f"Error occurred when generating full resume: {str(e)}")
        raise GeneralServerError(error_detail_message="Sorry could not generate the response at this moment. Please retry later")


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_cover_letter_handler(
    extracted_job_posting_details: ExtractedJobPostingDetails, resume_doc: UploadedDocument, supporting_docs: list[UploadedDocument] = None
) -> CoverLetterGenerationResponse:
    print("generate_cover_letter_handler runs")
    print("target llm:", TARGET_LLM_MODEL_HAIKU)

    # Prepare job details text
    extracted_full_job_posting_details_text = f"""
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

    # Prepare user prompt content blocks
    # add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "my base resume:"},
        prepare_document_for_claude(resume_doc),
    ]

    # add other supporting docs
    if supporting_docs:
        user_prompt_content_blocks.append({"type": "text", "text": "my additional professional context:"})
        for doc in supporting_docs:
            user_prompt_content_blocks.append(prepare_document_for_claude(doc))

    # add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details:"})
    user_prompt_content_blocks.append({"type": "text", "text": f"{extracted_full_job_posting_details_text}"})

    # add user instruction
    user_prompt_content_blocks.append({"type": "text", "text": cover_letter_gen_user_prompt})
    try:
        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL_HAIKU,
            system_prompt=cover_letter_gen_system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # Parse the response using our utility function
        llm_response_text = llm_response.content[0].text
        response_dict = parse_llm_json_response(llm_response_text)

        return CoverLetterGenerationResponse(
            cover_letter=response_dict.get("cover_letter", ""),
            applicant_name=response_dict.get("applicant_name", ""),
            company_name=extracted_job_posting_details.company_name,
            job_title_name=extracted_job_posting_details.job_title,
            location=extracted_job_posting_details.location,
        )

    except LLMResponseParsingError:
        print(traceback.format_exc())
        print("LLMResponseParsingError occurred")
        raise
    except Exception as e:
        print(f"Error occur when evalute job posting content: {str(e)}")
        raise GeneralServerError(error_detail_message="Sorry could not generate the response at this moment. Please retry later")


# ------------------------------------------------------------------------------------------------------------------------------


async def generate_application_question_answer_handler(
    extracted_job_posting_details: ExtractedJobPostingDetails,
    resume_doc: UploadedDocument,
    question: str,
    additional_requirements: Optional[str] = None,
    supporting_docs: Optional[List[UploadedDocument]] = None,
) -> ApplicationQuestionAnswerResponse:
    print("generate_application_question_answer_handler runs")
    print("target llm:", TARGET_LLM_MODEL_SONNET)

    # Prepare job details text
    extracted_full_job_posting_details_text = f"""
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

    # Prepare additional requirements text if provided
    additional_requirements_text = ""
    if additional_requirements:
        additional_requirements_text = additional_requirements.strip()

    application_question_user_prompt = application_question_user_prompt_template.format(
        question=question, additional_requirements_text=additional_requirements_text
    )

    # Prepare user prompt content blocks
    # Add resume
    user_prompt_content_blocks = [
        {"type": "text", "text": "my base resume"},
        prepare_document_for_claude(resume_doc),  # Handle resume with proper file type
    ]

    # Add other supporting docs if provided
    if supporting_docs:
        user_prompt_content_blocks.append({"type": "text", "text": "my additional professional context:"})
        for doc in supporting_docs:
            user_prompt_content_blocks.append(prepare_document_for_claude(doc))

    # Add job detail posting content
    user_prompt_content_blocks.append({"type": "text", "text": "Job posting details:"})
    user_prompt_content_blocks.append({"type": "text", "text": f"{extracted_full_job_posting_details_text}"})

    # Add user instruction with the application question
    user_prompt_content_blocks.append({"type": "text", "text": application_question_user_prompt})

    try:
        llm_response = await claude_message_api(
            model=TARGET_LLM_MODEL_SONNET,
            system_prompt=application_question_system_prompt,
            messages=[{"role": "user", "content": user_prompt_content_blocks}],
            temp=0.2,
            max_tokens=4000,
        )

        # Parse the response using our utility function
        llm_response_text = llm_response.content[0].text
        response_dict = parse_llm_json_response(llm_response_text)

        return ApplicationQuestionAnswerResponse(question=response_dict.get("question", question), answer=response_dict.get("answer", ""))

    except LLMResponseParsingError:
        print(traceback.format_exc())
        print("LLMResponseParsingError occurred")

        raise
    except Exception as e:
        print(f"Error occur when evalute job posting content: {str(e)}")
        raise GeneralServerError(error_detail_message="Sorry could not generate the response at this moment. Please retry later")
