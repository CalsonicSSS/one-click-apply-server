# Resume Tailor Assistant API

## Overview

Resume Tailor Assistant API is a FastAPI-based backend service that provides tailored resume suggestions and cover letter generation based on job posting details and user documents. The service leverages Anthropic's Claude AI models to process job descriptions and resumes to create professional recommendations.

## Features

- Extract job details from raw HTML content
- Analyze job postings to determine relevance
- Generate resume improvement suggestions
- Create a professionally tailored cover letter
- Handle various document types (PDF, DOCX, TXT)

## Tech Stack

- **FastAPI**: Backend framework for API development
- **Anthropic Claude API**: AI-powered text generation
- **Pydantic**: Data validation and settings management
- **CORS Middleware**: Secure API access configuration

## Project Structure

```
app/
├── main.py                          # FastAPI application entry point
├── config.py                        # Configuration settings using Pydantic
├── routes/
│   ├── suggestion_generation.py     # API routes for suggestion generation
├── services/
│   ├── suggestion_generation.py     # Business logic for tailoring resumes
├── utils/
│   ├── claude_handler/
│   │   ├── claude_config_apis.py    # Claude API integration
│   │   ├── claude_document_handler.py # Document handling for AI processing
│   │   ├── claude_prompts.py        # AI prompt templates
├── models/
│   ├── suggestion_generation.py     # Pydantic models for API request/response
```

## Installation

### Prerequisites

- Python 3.9+
- `pip` package manager
- `.env` file with required API keys and settings

### Steps

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd resume-tailor-api
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add the required API key for Claude and other settings:
     ```env
     CLAUDE_API_KEY=your_api_key_here
     ```
5. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Access the API documentation:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints

### Health Check

- **GET** `/health`
- Returns `{ "status": "healthy" }`

### Resume Tailoring

- **POST** `/api/v1/generation/cv-suggestions`
- **Request Body**:
  ```json
  {
    "raw_job_html_content": "<job description HTML>",
    "resume_doc": {
      "base64_content": "<base64 encoded resume>",
      "file_type": "application/pdf",
      "name": "resume.pdf"
    },
    "supporting_docs": [
      {
        "base64_content": "<base64 encoded document>",
        "file_type": "text/plain",
        "name": "cover_letter.txt"
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "resume_suggestions": [
      {
        "where": "Experience section",
        "suggestion": "Add quantifiable achievements in your role at XYZ Corp",
        "reason": "This strengthens alignment with job requirements."
      }
    ],
    "cover_letter": "Full generated cover letter text"
  }
  ```

## Environment Variables

| Variable        | Description                          |
| --------------- | ------------------------------------ |
| CLAUDE_API_KEY  | API key for Anthropic Claude service |
| ALLOWED_ORIGINS | CORS settings for allowed origins    |

## Contribution

1. Fork the repository
2. Create a feature branch
3. Commit changes and push to your fork
4. Open a pull request

## License

MIT License. See `LICENSE` for details.
