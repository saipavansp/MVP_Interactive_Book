import streamlit as st
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import google.generativeai as genai
from typing import Dict, List, Tuple
from datetime import datetime

# Configure Gemini API using Streamlit secrets
if 'GOOGLE_API_KEY' not in st.secrets:
    st.error('Google API key not found. Please add your API key to the Streamlit secrets.')
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error(f"Error configuring Google API: {str(e)}")
    st.stop()


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_buffer):
        try:
            pdf_reader = PyPDF2.PdfReader(file_buffer)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None


class APIHandler:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Error initializing Gemini model: {str(e)}")
            raise e

    def get_enhanced_response(self,
                              query: str,
                              context: str,
                              book_response: str) -> str:
        try:
            prompt = f"""
            Context from the book:
            {context}

            Initial response based on book content:
            {book_response}

            User question:
            {query}

            Please provide a comprehensive answer that:
            1. Primarily uses the book's content
            2. Enhances the response with additional relevant information
            3. Maintains accuracy and relevance to the original question
            4. Clearly distinguishes between book content and additional information
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            st.warning(f"API Error: {str(e)}")
            return book_response


class InteractiveBook:
    def __init__(self, book_content: str):
        self.raw_content = book_content
        self.sentences = [s.strip() for s in book_content.split('.') if s.strip()]
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.sentences)
        self.api_handler = APIHandler()

    def find_relevant_context(self, query: str, n_sentences: int = 3) -> str:
        try:
            query_vector = self.vectorizer.transform([query])
            similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix)
            top_indices = similarity_scores[0].argsort()[-n_sentences:][::-1]
            return ' '.join([self.sentences[i] for i in top_indices])
        except Exception as e:
            st.error(f"Error finding context: {str(e)}")
            return ""

    def generate_response(self, query: str, context: str) -> Dict[str, str]:
        book_response = f"Based on the book content: {context}"

        try:
            enhanced_response = self.api_handler.get_enhanced_response(
                query=query,
                context=context,
                book_response=book_response
            )
            return {
                "book_response": book_response,
                "enhanced_response": enhanced_response
            }
        except Exception as e:
            return {
                "book_response": book_response,
                "enhanced_response": None,
                "error": str(e)
            }


def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_doc' not in st.session_state:
        st.session_state.current_doc = None
    if 'interactive_book' not in st.session_state:
        st.session_state.interactive_book = None


def display_document_stats(content: str):
    """Display document statistics in the sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Document Statistics")
    st.sidebar.write(f"Total characters: {len(content)}")
    st.sidebar.write(f"Total words: {len(content.split())}")
    st.sidebar.write(f"Total sentences: {len([s for s in content.split('.') if s.strip()])}")


def handle_file_upload(file, file_type):
    """Process uploaded file and return content"""
    try:
        if file_type == "PDF":
            with st.spinner("Processing PDF file..."):
                content = DocumentProcessor.extract_text_from_pdf(file)
        else:
            content = file.getvalue().decode("utf-8")

        if not content:
            st.error("Could not extract text from the document.")
            return None

        return content
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None


def main():
    st.title("📚 Interactive Book AI")

    # Initialize session state
    initialize_session_state()

    # Sidebar for document upload
    st.sidebar.title("Document Upload")
    file_type = st.sidebar.selectbox("Select file type:", ["PDF", "TXT"])
    allowed_types = ['pdf'] if file_type == "PDF" else ['txt']
    file = st.sidebar.file_uploader(f"Upload your {file_type} file", type=allowed_types)

    # Clear chat button in sidebar
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

    # New document button in sidebar
    if st.sidebar.button("New Document"):
        st.session_state.clear()
        st.experimental_rerun()

    if file is not None:
        # Check if it's a new document
        if st.session_state.current_doc != file.name:
            content = handle_file_upload(file, file_type)
            if content:
                st.session_state.current_doc = file.name
                st.session_state.interactive_book = InteractiveBook(content)
                display_document_stats(content)
                st.success("Document processed successfully!")

        if st.session_state.interactive_book:
            st.write("Chat with your document! Ask questions about the content.")

            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # Chat input
            user_input = st.chat_input("Ask your question here...")

            if user_input:
                # Add user message
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                with st.chat_message("user"):
                    st.write(user_input)

                # Generate response
                with st.spinner("Generating response..."):
                    context = st.session_state.interactive_book.find_relevant_context(user_input)
                    responses = st.session_state.interactive_book.generate_response(user_input, context)

                with st.chat_message("assistant"):
                    if responses.get("enhanced_response"):
                        st.write(responses["enhanced_response"])
                        with st.expander("Show book-only response"):
                            st.write(responses["book_response"])
                    else:
                        st.write(responses["book_response"])

                # Add assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": responses.get("enhanced_response") or responses["book_response"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    else:
        st.info("Please upload a PDF or TXT file to start chatting!")


if __name__ == "__main__":
    main()