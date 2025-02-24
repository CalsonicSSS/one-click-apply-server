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
    If it is not a job posting detail related site, output your response in JSON format as:
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
    1. Analyze both the job posting details and the user's base resume/supporting documents as professional background information
    2. Identify 2-4 key places (or as you see fit) in the resume where tailored and relevant changes would improve the chance of passing through Applicant Tracking Systems (ATS)
    3. Generate specific, tailored resume suggestions from your identifications:
       - Incorporate relevant keywords from the job posting
       - Quantify achievements where possible (e.g., "Increased data processing efficiency by 30% through automation")
       - Highlight the most relevant experiences and skills that match the job requirements
    4. Create a one-page professional cover letter that:
       - Uses the same tone as the user's existing documents as much as possible
       - Showcases the user's relevant experience and skills
       - Highlights the candidate's most relevant qualifications
       - Expresses enthusiasm for the position
    5. Review and make sure all your suggestions and generation are targeted to the job posting details and based on user's given base resume and other docs
    
    Your suggestions should be specific, practical, and targeted to make the resume more appealing for this particular job.
    """


suggestion_generation_user_prompt = f"""
        Based on the job posting detail given and my documents as background:
        
        1. Provide 2-4 specific places in my resume to tailor, with:
           - suggested new changes  
           - short indication where it is in my original resume for each
           - A brief explanation / reason why this change will help as reason for each
           - Do not exagerrate too much in terms of suggestion and quantification, keep it professional after all.

           
        2. Generate a professional, tailored one-page cover letter that:
           - Matches my writing style/tone.
           - Emphasizes my relevant experience and make it appealing for this specific job posting.
           - Addresses the specific needs from the job posting relevant to my given base resume and other docs.
           - Do not exagerrate too much, keep it professional after all.
           - format cover letter properly such as header, body, and closing, new line other as you see fit. 
        
        Output requirement:
        
        - Make sure your only output is the pure JSON structure below 
        - the structure follows: "resume_suggestions" and "cover_letter". The resume_suggestions field is a list of dictionaries, each contains "where", "suggestion", and "reason" fields.
        - Make sure all the output in the JSON are properly formatted, and all special characters are properly escaped and handled (if there is any) as we will directly use this JSON output for further conversion later.
        - Do not include any other information in your response.

        {{
            "resume_suggestions": [
                {{
                    "where": "where to replace original text from my resume",
                    "suggestion": "Your tailored suggestion change",
                    "reason": "Explanation of why this change helps"
                }},
                ...
            ],
            "cover_letter": "Full text of the tailored cover letter"
        }}
        """
