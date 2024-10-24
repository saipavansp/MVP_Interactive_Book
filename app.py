import streamlit as st
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import google.generativeai as genai
from typing import Dict, List, Tuple
from datetime import datetime
import os



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
            raise Exception(f"Error processing PDF: {str(e)}")


class APIHandler:
    def __init__(self):
        # Initialize Gemini Pro model
        self.model = genai.GenerativeModel('gemini-pro')

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
            return f"API Error: {str(e)}\nFalling back to book-based response:\n{book_response}"


class InteractiveBook:
    def __init__(self, book_content: str):
        self.raw_content = book_content
        self.sentences = [s.strip() for s in book_content.split('.') if s.strip()]
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.sentences)
        self.api_handler = APIHandler()

    def find_relevant_context(self, query: str, n_sentences: int = 3) -> str:
        query_vector = self.vectorizer.transform([query])
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix)
        top_indices = similarity_scores[0].argsort()[-n_sentences:][::-1]
        return ' '.join([self.sentences[i] for i in top_indices])

    def generate_response(self, query: str, context: str) -> Dict[str, str]:
        # Generate basic response from book
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


def main():
    st.title("📚Interactive AI Book")

    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        st.error("Google API Key not found in environment variables. Please check your .env file.")
        return

    # File Upload
    st.sidebar.title("Document Upload")
    file_type = st.sidebar.selectbox("Select file type:", ["PDF", "TXT"])
    allowed_types = ['pdf'] if file_type == "PDF" else ['txt']
    file = st.sidebar.file_uploader(f"Upload your {file_type} file", type=allowed_types)

    if file is not None:
        try:
            # Process document
            if file_type == "PDF":
                with st.spinner("Processing PDF file..."):
                    content = DocumentProcessor.extract_text_from_pdf(file)
            else:
                content = file.getvalue().decode("utf-8")

            # Initialize Interactive Book
            if 'interactive_book' not in st.session_state:
                with st.spinner("Processing content..."):
                    st.session_state.interactive_book = InteractiveBook(content)
                    st.sidebar.success("Document processed successfully!")

            # Display document statistics
            st.sidebar.markdown("---")
            st.sidebar.subheader("Document Statistics")
            st.sidebar.write(f"Total characters: {len(content)}")
            st.sidebar.write(f"Total words: {len(content.split())}")

            # Chat Interface
            st.write("Chat with your document! Ask questions about the content.")

            # Initialize chat history
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []

            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # Chat input
            user_input = st.chat_input("Ask your question here...")

            if user_input:
                # Add user message to chat
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
                    if responses["enhanced_response"]:
                        st.write(responses["enhanced_response"])
                        if st.checkbox("Show book-only response"):
                            st.write("Book response:", responses["book_response"])
                    else:
                        st.write(responses["book_response"])

                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": responses["enhanced_response"] or responses["book_response"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload a PDF or TXT file to start chatting!")

    # Clear chat button
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()


if __name__ == "__main__":
    main()