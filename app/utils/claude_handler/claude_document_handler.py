import base64
from io import BytesIO
from typing import Dict, Any
from docx import Document
from PyPDF2 import PdfReader
from app.models.uploaded_doc import UploadedDocument
from app.custom_exceptions import FileTypeNotSupportedError, GeneralServerError


import base64
from typing import Dict, Any
from app.models.uploaded_doc import UploadedDocument
from app.custom_exceptions import FileTypeNotSupportedError, GeneralServerError


def prepare_document_for_claude(doc: UploadedDocument) -> Dict[str, Any]:
    """
    Prepares a document for Claude API using native PDF support.
    Claude now handles PDF parsing directly with full vision capabilities.

    Args:
        doc: UploadedDocument containing base64 content, file type, and name

    Returns:
        Dict with proper format for Claude API document block
    """
    try:
        # Only accept PDF files now
        if doc.file_type != "application/pdf":
            raise FileTypeNotSupportedError(
                error_detail_message=f"{doc.name} file type '{doc.file_type}' is not supported. Only PDF files are accepted."
            )

        # Return document in Claude's native PDF format
        # Claude will handle all parsing internally with vision capabilities
        return {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": doc.base64_content},  # Already base64 encoded from frontend
        }

    except FileTypeNotSupportedError:
        # Re-raise our custom error
        raise

    except Exception as e:
        print(f"Error processing document {doc.name}: {str(e)}")
        raise GeneralServerError(error_detail_message=f"Something went wrong while processing your document: {doc.name}")
