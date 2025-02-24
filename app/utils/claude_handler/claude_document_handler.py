import base64
from io import BytesIO
from typing import Dict, Any
from docx import Document
from PyPDF2 import PdfReader
from app.models.suggestion_generation import UploadedDocument


def prepare_document_for_claude(doc: UploadedDocument) -> Dict[str, Any]:
    """
    Prepares a document for Claude API based on its file type.
    """
    try:
        # Decode the base64 content to binary
        binary_content = base64.b64decode(doc.base64_content)

        if doc.file_type == "application/pdf":
            # Extract text from PDF
            pdf_file = BytesIO(binary_content)
            reader = PdfReader(pdf_file)
            full_extracted_text = ""
            for page in reader.pages:
                full_extracted_text += "page1:" + "\n" + page.extract_text() + "\n\n"
            return {"type": "text", "text": full_extracted_text}

        elif doc.file_type == "text/plain":
            # For TXT files, simply decode to text
            full_extracted_text = binary_content.decode("utf-8")
            return {"type": "text", "text": full_extracted_text}

        elif doc.file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Handle DOCX
            doc_file = BytesIO(binary_content)
            document = Document(doc_file)

            all_extracted_components = []

            # Extract text from paragraphs
            for paragraph in document.paragraphs:
                all_extracted_components.append(paragraph.text)

            # Extract text from tables
            for table in document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        all_extracted_components.append(cell.text)

            # Extract text from headers and footers
            for section in document.sections:
                for header in section.header.paragraphs:
                    all_extracted_components.append(header.text)
                for footer in section.footer.paragraphs:
                    all_extracted_components.append(footer.text)

            full_extracted_text = "\n\n".join(all_extracted_components)
            return {"type": "text", "text": full_extracted_text}

        else:
            raise ValueError(f"Unsupported file type: {doc.file_type}")

    except Exception as e:
        print(f"Error processing document {doc.name}: {str(e)}")
        return {"type": "text", "text": f"Error processing document {doc.name}: {str(e)}"}
