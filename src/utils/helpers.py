from datetime import datetime
from typing import Dict

def format_chat_message(role: str, content: str) -> Dict[str, str]:
    """Format chat message with timestamp"""
    return {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def validate_file_type(filename: str, allowed_extensions: list) -> bool:
    """Validate file extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size(file_buffer) -> int:
    """Get file size in bytes"""
    file_buffer.seek(0, 2)  # Seek to end
    size = file_buffer.tell()
    file_buffer.seek(0)  # Reset position
    return size