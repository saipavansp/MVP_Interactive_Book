from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from ..api.gemini_handler import GeminiHandler


class ChatEngine:
    def __init__(self, content: str):
        self.raw_content = content
        self.sentences = [s.strip() for s in content.split('.') if s.strip()]
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.sentences)
        self.api_handler = GeminiHandler()

    def find_relevant_context(self, query: str, n_sentences: int = 3) -> str:
        query_vector = self.vectorizer.transform([query])
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix)
        top_indices = similarity_scores[0].argsort()[-n_sentences:][::-1]
        return ' '.join([self.sentences[i] for i in top_indices])

    def generate_response(self, query: str, context: str) -> Dict[str, str]:
        try:
            response_data = self.api_handler.generate_response(query, context)

            if "error" not in response_data:
                return {
                    "book_response": response_data["book_response"],
                    "additional_info": response_data["additional_info"],
                    "combined_response": response_data["combined_response"],
                    "context": context
                }
            else:
                return {
                    "error": response_data["error"],
                    "context": context
                }
        except Exception as e:
            return {
                "error": str(e),
                "context": context
            }