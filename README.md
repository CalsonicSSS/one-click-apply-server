# Ninja Craft Server

Backend API service for the Ninja Craft Chrome extension, providing AI-powered job application assistance using FastAPI and Anthropic's Claude models.

## Overview

This server provides the intelligence behind the Ninja Craft Chrome extension, using Anthropic's Claude AI models to:

- Analyze job posting content
- Generate tailored resume suggestions
- Create personalized cover letters
- Craft responses to application questions

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, high-performance web framework
- **Language**: Python 3.9+
- **AI Integration**: [Anthropic Claude API](https://www.anthropic.com/claude)
- **Validation**: [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management
- **Document Processing**:
  - PyPDF2 - PDF parsing
  - python-docx - DOCX parsing

## Project Structure

```
app/
├── config.py                 # Application configuration using Pydantic
├── constants.py              # Application constants
├── custom_exceptions.py      # Custom HTTP exceptions
├── main.py                   # FastAPI application entry point
├── models/                   # Pydantic models for request/response validation
│   ├── application_question.py
│   ├── cover_letter.py
│   ├── job_posting_eval.py
│   ├── resume_suggestions.py
│   └── uploaded_doc.py
├── routes/                   # API route definitions
│   └── suggestion_generation.py
├── services/                 # Business logic
│   └── suggestion_generation.py
└── utils/                    # Utility functions
    └── claude_handler/       # Claude API integration utilities
        ├── claude_config_apis.py
        ├── claude_document_handler.py
        └── claude_prompts.py
```

## API Endpoints

The server exposes the following endpoints under the `/api/v1/generation` prefix:

| Endpoint                       | Method | Description                                                                   |
| ------------------------------ | ------ | ----------------------------------------------------------------------------- |
| `/job-posting/evaluate`        | POST   | Analyzes HTML content to determine if it's a job posting and extracts details |
| `/resume/suggestions-generate` | POST   | Generates tailored resume suggestions based on job posting and user's resume  |
| `/cover-letter/generate`       | POST   | Creates a personalized cover letter for a specific job                        |
| `/application-question/answer` | POST   | Generates responses to application questions                                  |

## Setup and Installation

### Prerequisites

- Python 3.9+
- Anthropic API key

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Ninja-craft-server.git
   cd Ninja-craft-server
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   CLAUDE_API_KEY=your_anthropic_api_key
   ```

### Running the Application

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Adding New Features

1. Define new models in the `app/models` directory
2. Add service functions in `app/services`
3. Create new endpoints in `app/routes`

### Error Handling

The application uses custom exceptions defined in `app/custom_exceptions.py` for consistent error handling across the API. Main exception types:

- `GeneralServerError`: For general 500 server errors
- `FileTypeNotSupportedError`: For unsupported document formats
- `NoneJobSiteError`: When a provided page is not a job posting

## Document Processing

The server supports the following document formats:

- PDF (application/pdf)
- Word Documents (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- Plain Text (text/plain)

Documents are uploaded by the client as base64-encoded strings and processed using the appropriate library based on file type.

## AI Integration

The application uses Anthropic's Claude models with carefully crafted prompts to generate high-quality, contextually relevant content. The models are configured in `app/constants.py` and currently default to using Claude 3.5 Haiku.

## Security Considerations

- **CORS**: The application is configured to accept requests from authorized origins
- **Input Validation**: All input is validated using Pydantic models
- **Error Handling**: Custom exceptions provide secure error responses

## Environment Variables

| Variable          | Description                  | Default                            |
| ----------------- | ---------------------------- | ---------------------------------- |
| `CLAUDE_API_KEY`  | Anthropic API key (required) | None                               |
| `ALLOWED_ORIGINS` | CORS allowed origins         | ["*"] (all origins in development) |

## License

This project is licensed under the [MIT License](LICENSE).
