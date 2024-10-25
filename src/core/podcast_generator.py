import google.generativeai as genai
import streamlit as st
from typing import Dict, List  # Removed Optional since it's unused


class PodcastGenerator:
    def __init__(self):
        """Initialize the PodcastGenerator with Gemini model"""
        try:
            if not st.secrets.get("GOOGLE_API_KEY"):
                raise ValueError("Google API key not found in secrets")

            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            self.model = genai.GenerativeModel('gemini-pro')

            if not self.model:
                raise ValueError("Failed to initialize Gemini model")

            if 'debug_log' not in st.session_state:
                st.session_state['debug_log'] = []

        except Exception as e:
            st.error(f"Error initializing Gemini model: {str(e)}")
            raise e

    @staticmethod
    def _log_debug(message: str):
        """Add debug message to log"""
        if 'debug_log' not in st.session_state:
            st.session_state['debug_log'] = []
        st.session_state['debug_log'].append(message)

    def generate_chapter_topics(self, content: str) -> List[Dict]:
        """Generate topics with detailed debugging"""
        try:
            self._log_debug("Starting topic generation...")

            if not content or len(content.strip()) < 100:
                st.warning("Content is too short for topic generation")
                return []

            prompt = f"""
            Create 3 clear podcast discussion topics from this academic content.

            USE EXACTLY THIS FORMAT FOR EACH TOPIC:
            Title: [Short title for the topic]
            Description: [One sentence description]
            Key Points:
            - First key point
            - Second key point
            - Third key point

            Content to analyze:
            {content[:2000]}
            """

            self._log_debug("Sending prompt to model...")

            try:
                response = self.model.generate_content(prompt)
                if not response:
                    self._log_debug("No response from model")
                    return []

                self._log_debug(f"Received response: {response.text[:100]}...")

            except Exception as e:
                self._log_debug(f"Model generation error: {str(e)}")
                return []

            topics = self._simple_parse_topics(response.text)
            self._log_debug(f"Parsed {len(topics)} topics")

            if not topics:
                self._log_debug("No topics parsed from response")
                return []

            return topics

        except Exception as e:
            self._log_debug(f"Error in generate_chapter_topics: {str(e)}")
            st.error(f"Error generating topics: {str(e)}")
            return []

    def _simple_parse_topics(self, text: str) -> List[Dict]:
        """Simplified topic parsing with error handling"""
        try:
            self._log_debug("Starting simple topic parsing...")

            topics = []
            current_topic = {}
            current_key_points = []

            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('Title:'):
                    if current_topic and 'title' in current_topic:
                        if current_key_points:
                            current_topic['key_points'] = current_key_points
                        topics.append(current_topic.copy())
                        current_topic = {}
                        current_key_points = []
                    current_topic['title'] = line[6:].strip()

                elif line.startswith('Description:'):
                    current_topic['description'] = line[12:].strip()

                elif line.startswith('- '):
                    current_key_points.append(line[2:].strip())

            if current_topic and 'title' in current_topic:
                if current_key_points:
                    current_topic['key_points'] = current_key_points
                topics.append(current_topic.copy())

            self._log_debug(f"Successfully parsed {len(topics)} topics")
            return topics

        except Exception as e:
            self._log_debug(f"Error in simple topic parsing: {str(e)}")
            return []

    def generate_podcast_script(self, content: str, style: str = "conversational") -> Dict:
        """Generate podcast-style conversation"""
        try:
            styles = {
                "conversational": "casual, friendly, and engaging",
                "educational": "informative, clear, with detailed explanations",
                "storytelling": "narrative-driven, with examples and analogies",
                "interview": "professional interview style with probing questions"
            }

            prompt = f"""
            Transform this content into a dynamic podcast conversation between a Host and an Expert.
            Style: {styles.get(style, styles['conversational'])}

            Content to transform:
            {content[:4000]}

            Create a natural conversation that follows these guidelines:
            1. Host should:
               - Ask thoughtful questions
               - Guide the conversation
               - Follow up on interesting points
               - Use natural transitions

            2. Expert should:
               - Provide clear explanations
               - Use relevant examples
               - Break down complex ideas
               - Connect concepts together

            Format as:
            Host: [Question/Comment]
            Expert: [Response/Explanation]
            """

            response = self.model.generate_content(prompt)
            conversation = self._parse_conversation(response.text)

            return {
                "status": "success",
                "conversation": conversation,
                "style": style
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def _parse_conversation(text: str) -> List[Dict]:
        """Parse the conversation with metadata"""
        lines = text.strip().split('\n')
        conversation = []
        current_speaker = None
        current_text = []
        segment_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Host:'):
                if current_speaker:
                    segment_count += 1
                    conversation.append({
                        'role': current_speaker,
                        'content': ' '.join(current_text),
                        'segment': segment_count,
                        'type': 'question' if current_speaker == 'host' else 'explanation'
                    })
                current_speaker = 'host'
                current_text = [line[5:].strip()]
            elif line.startswith('Expert:'):
                if current_speaker:
                    segment_count += 1
                    conversation.append({
                        'role': current_speaker,
                        'content': ' '.join(current_text),
                        'segment': segment_count,
                        'type': 'question' if current_speaker == 'host' else 'explanation'
                    })
                current_speaker = 'expert'
                current_text = [line[7:].strip()]
            else:
                current_text.append(line)

        if current_speaker and current_text:
            segment_count += 1
            conversation.append({
                'role': current_speaker,
                'content': ' '.join(current_text),
                'segment': segment_count,
                'type': 'question' if current_speaker == 'host' else 'explanation'
            })

        return conversation

    @staticmethod
    def display_debug_info():
        """Display debug information in Streamlit"""
        if 'debug_log' in st.session_state and st.session_state['debug_log']:
            with st.expander("🔍 Debug Information"):
                for log in st.session_state['debug_log']:
                    st.write(log)