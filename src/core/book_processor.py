import PyPDF2
from typing import Optional, Dict


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_buffer) -> Optional[str]:
        try:
            pdf_reader = PyPDF2.PdfReader(file_buffer)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    @staticmethod
    def process_text_file(file_buffer) -> str:
        try:
            return file_buffer.getvalue().decode("utf-8")
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")

    @staticmethod
    def get_document_stats(content: str) -> Dict[str, int]:
        return {
            "total_chars": len(content),
            "total_words": len(content.split()),
            "total_sentences": len([s for s in content.split('.') if s.strip()])
        }