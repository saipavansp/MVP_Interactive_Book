class Settings:
    # App settings
    APP_TITLE = "📚 Interactive Book AI"
    APP_DESCRIPTION = "Chat with your documents using AI"

    # File settings
    ALLOWED_EXTENSIONS = ['pdf', 'txt']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Model settings
    DEFAULT_RESPONSE_LENGTH = 3

    # Error messages
    ERROR_MESSAGES = {
        "file_type": "Invalid file type. Please upload a PDF or TXT file.",
        "file_size": "File size too large. Maximum size is 10MB.",
        "api_error": "Error connecting to AI service. Please try again.",
        "processing_error": "Error processing document. Please try again."
    }