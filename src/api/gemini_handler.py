import streamlit as st
import google.generativeai as genai
from typing import Optional, Dict


class GeminiHandler:
    def __init__(self):
        try:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Error initializing Gemini API: {str(e)}")
            raise e

    def generate_response(self, query: str, context: str) -> Dict[str, str]:
        try:
            # First response based on book content
            book_prompt = f"""
            Context from the book:
            {context}

            User question:
            {query}

            Provide a response using only the book's content.
            """
            book_response = self.model.generate_content(book_prompt).text

            # Additional knowledge from Gemini
            additional_prompt = f"""
            Question: {query}

            Provide additional relevant information and examples beyond the book's content.
            Make sure to enhance understanding while staying relevant to the topic.
            """
            additional_info = self.model.generate_content(additional_prompt).text

            # Combined response
            final_prompt = f"""
            Book's response: {book_response}

            Additional information: {additional_info}

            Create a comprehensive response that:
            1. Clearly distinguishes between book content and additional information
            2. Integrates both sources naturally
            3. Maintains flow and readability
            4. Adds relevant examples where appropriate
            """
            final_response = self.model.generate_content(final_prompt).text

            return {
                "book_response": book_response,
                "additional_info": additional_info,
                "combined_response": final_response
            }

        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return {
                "error": str(e)
            }