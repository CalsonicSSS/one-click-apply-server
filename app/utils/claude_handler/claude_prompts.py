html_eval_system_prompt = """
You are an expert system that can raw analyze HTML content and determine if it's a job posting/description related page.
Your task is to:
1. Determine if the HTML content represents a job posting page
2. Think thoroughly with reason for your determination
3. If it is a job posting, extract all relevant information including as much of the following as possible:
    - Job title
    - Company name
    - Job description
    - Responsibilities
    - Requirements/qualifications
    - Location
    - Any other relevant details

Follow these guidelines:
- Focus on recognizing common patterns in job posting pages
- Pages with detailed job descriptions, requirements, responsibilities are job postings
- Pages with application forms without detailed job info are likely not proper job postings
- Pages completely unrelated to jobs posting detils (e.g., news, blogs) are not job postings
"""


def html_eval_user_prompt_generator(raw_html_content: str):
    return f"""
Analyze the following HTML content for me and determine if it's a job posting page.
If it is not a job posting detail related site, output your response in JSON format directly as:
{{
    "is_job_posting": False,
    "extracted_job_details": None
}} 
    
If it is a proper job posting site, first extract all relevant job information from the raw html content, and fill in below field as much as possible.
{{
    "is_job_posting": True,
    "extracted_job_details": {{
        "job_title": "",
        "company_name": "",
        "job_description": "",
        "responsibilities": [],
        "requirements": [],
        "location": "",
        "other_additional_details": ""
    }}
}}

Output requirement:
- Make sure your only output is the pure JSON structure above with these seven fields. 
- Make sure all the output in the JSON are properly formatted, and all special characters are properly handled (if there is any) as we will directly use this JSON output for further conversion later.
- Do not include any other information in your response.
- If any of the fields are not available in the HTML content, leave them as empty strings or lists as default.


HTML Content:
{raw_html_content}
"""


suggestion_generation_system_prompt = """
You are an expert resume and cover letter tailoring assistant. Your task is to generate precise, tailored suggestions for a job applicant's resume and create a professional cover letter, all tailored to the given specific job posting in this message.

Your goal is to:
1. Analyze the given job posting details  
2. Go through the user's base resume and supporting documents (if available), which will be provided as extracted text from (PDF, TXT or DOCX). Identify and categorize key sections, and structures.  
3. Identify 3 key places (or as you see fit) in the resume where relevant tailored changes would improve the chance of passing through Applicant Tracking Systems (ATS) for this posting.
4. Generate specific, tailored resume suggestions from your identifications:
    - Incorporate relevant keywords from the job posting
    - Quantify achievements where possible (e.g., "Increased data processing efficiency by 30% through automation")
    - Highlight the most relevant experiences and skills that match the job requirements
5. Create a one-page long professional cover letter that:
    - Uses the same tone as the user's existing documents as much as possible
    - Showcases the user's relevant experience and skills to the job posting
    - Highlights the candidate's most relevant qualifications to the job posting
    - Expresses enthusiasm for the position
    - Do not exagerrate too much, keep it professional after all.
6. Finally, make sure generated output handles and escapes control or special characters properly while preserving formatting. 

Your suggestions should be specific, practical, and targeted to make the resume more appealing for this particular job.
"""


suggestion_generation_user_prompt = f"""
Based on the job posting detail and my professional background, help me with the following:

1. Provide some specific tailored suggestion changes (4) in my base resume:
   - Aim to pass ATS for this job posting.
   - Quantify achievements where possible (e.g., "Increased data processing efficiency by 30% through automation").
   - Provide a brief reason why each change will help.
   - Indicate where or which section in my original resume each suggestion applies to.
   - Ensure the suggested text length closely matches the original; avoid lengthy suggestions.
   - Do not exaggerate; keep suggestions professional and realistic.

2. **Generate a professional, one-page, tailored cover letter in a pre-formatted string format.**  
   - Ensure the cover letter follows this structure:
        - **Header:** My name, phone number, email (if available) each in 3 different line (MUST).
        - **Opening Paragraph:** State the job position and briefly explain why I am a suitable candidate.
        - **Main Content:** 
            - Provide paragraph(s) with detailed introduciton and thoroughly stating my relevant experience, skills, examples, and achievements relevant to this posting.
            - Fully utilize my background context and all key points from my resume to generate
            - Give concrete example(s) for demonstrating how my background and skills aligns with the job requirements. Using story-telling style.
            - You MAY give a few bullets for highlighting relevant points of mine related to this job posting for better readability (you do not have to if you don't see the need) 
        - **Closing Paragraph:** Express enthusiasm for the role, state availability for an interview, and thank them for considering my application about company for this posting.
        - **sign_off:**  "Sincerely," 
        - **signature:** "First_Name Last_Name"
    - Make sure the cover letter fully utilize most of key points and experiences from my base resume and any other supporting docs if available and make it tailor more to the job posting (MUST)
    - Make sure the length fill up to whole one-page length 

Output requirements:

- Ensure your response is a pure JSON structure as outlined below, without additional data.
- The structure includes: "company_name", "job_title_name", "applicant_name", "resume_suggestions", and "cover_letter" as fields.
- The "resume_suggestions" field is a list of dictionaries, each containing "where", "suggestion", and "reason" fields.
- Ensure the text output is properly formatted, with all special and control characters correctly escaped and handled, making it valid for `json.loads()` in Python.

{{
    "company_name": "the company name",
    "job_title_name": "job title name",
    "applicant_name": "my name (in the format 'first name_last name')",
    "resume_suggestions": [
        {{
            "where": "section of the resume to modify",
            "suggestion": "tailored suggestion (concise)",
            "reason": "explanation of why this change is beneficial"
        }},
        ...
    ],
    "cover_letter": "Full formatted text content of the tailored cover letter following above cover rules"
}}
"""
