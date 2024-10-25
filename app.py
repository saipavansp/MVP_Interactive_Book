import streamlit as st
from src.core.book_processor import DocumentProcessor
from src.core.chat_engine import ChatEngine
from src.core.podcast_generator import PodcastGenerator
from src.utils.helpers import format_chat_message, get_file_size
from src.config.settings import Settings


def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_doc' not in st.session_state:
        st.session_state.current_doc = None
    if 'chat_engine' not in st.session_state:
        st.session_state.chat_engine = None
    if 'document_stats' not in st.session_state:
        st.session_state.document_stats = None
    if 'podcast_generator' not in st.session_state:
        try:
            st.session_state.podcast_generator = PodcastGenerator()
        except Exception as init_error:
            st.error(f"Failed to initialize podcast generator: {str(init_error)}")
            st.session_state.podcast_generator = None
    if 'podcast_conversation' not in st.session_state:
        st.session_state.podcast_conversation = None
    if 'topics' not in st.session_state:
        st.session_state.topics = None
    if 'document_content' not in st.session_state:
        st.session_state.document_content = None
    if 'debug_log' not in st.session_state:
        st.session_state.debug_log = []


def display_document_stats(stats: dict):
    """Display document statistics in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Document Statistics")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Characters", f"{stats['total_chars']:,}")
        st.metric("Sentences", f"{stats['total_sentences']:,}")
    with col2:
        st.metric("Words", f"{stats['total_words']:,}")
        reading_time = round(stats['total_words'] / 200)  # Average reading speed
        st.metric("Reading Time", f"{reading_time} min")


def handle_file_upload(file, file_type: str):
    """Process uploaded file and return content"""
    try:
        # Validate file size
        file_size = get_file_size(file)
        if file_size > Settings.MAX_FILE_SIZE:
            st.error(Settings.ERROR_MESSAGES["file_size"])
            return None

        # Process file based on type
        if file_type == "PDF":
            with st.spinner("📄 Processing PDF file..."):
                content = DocumentProcessor.extract_text_from_pdf(file)
        else:
            content = DocumentProcessor.process_text_file(file)

        if not content:
            st.error("Could not extract text from the document.")
            return None

        return content
    except Exception as upload_error:
        st.error(f"Error processing file: {str(upload_error)}")
        return None


def display_podcast_interface():
    """Display enhanced podcast generation interface"""
    try:
        # Force initialize podcast generator if it doesn't exist or failed
        try:
            if not st.session_state.get('podcast_generator'):
                st.session_state.podcast_generator = PodcastGenerator()
        except Exception as init_error:
            st.error(f"Failed to initialize podcast generator: {str(init_error)}")
            return

        if not st.session_state.document_content:
            st.warning("Please upload a document first.")
            return

        st.markdown("### 🎙️ Podcast Generator")

        # Style selection
        style = st.select_slider(
            "Select Conversation Style",
            options=["conversational", "educational", "storytelling", "interview"],
            value="educational",  # Default for academic content
            format_func=lambda x: {
                "conversational": "👥 Casual & Engaging",
                "educational": "📚 Educational & Detailed",
                "storytelling": "📖 Story-Driven",
                "interview": "🎤 Professional Interview"
            }[x]
        )

        # Generate topics with error handling
        if not st.session_state.get('topics'):
            with st.spinner("🎯 Identifying discussion topics..."):
                try:
                    podcast_gen = st.session_state.podcast_generator
                    if podcast_gen is None:
                        st.error("Podcast generator not initialized properly")
                        return

                    topics = podcast_gen.generate_chapter_topics(
                        st.session_state.document_content
                    )
                    if topics:
                        st.session_state.topics = topics
                        st.success("Topics generated successfully!")
                    else:
                        st.error("Could not generate topics. Please try again.")
                        if hasattr(podcast_gen, 'display_debug_info'):
                            podcast_gen.display_debug_info()
                        return
                except Exception as topic_error:
                    st.error(f"Error generating topics: {str(topic_error)}")
                    return

        # Display topics
        if st.session_state.get('topics'):
            st.markdown("#### 📋 Episode Segments")
            for i, topic in enumerate(st.session_state.topics, 1):
                with st.expander(f"Segment {i}: {topic['title']}", expanded=True):
                    st.markdown(f"**Description:** {topic['description']}")
                    st.markdown("**Key Discussion Points:**")
                    for point in topic['key_points']:
                        st.markdown(f"- {point}")

        # Generation controls
        st.markdown("---")
        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("🎙️ Generate Podcast Conversation", use_container_width=True):
                with st.spinner("🎬 Creating engaging conversation..."):
                    try:
                        result = st.session_state.podcast_generator.generate_podcast_script(
                            st.session_state.document_content,
                            style
                        )

                        if result["status"] == "success":
                            st.session_state.podcast_conversation = result["conversation"]
                            st.success("Podcast conversation generated successfully!")
                        else:
                            st.error(f"Error generating conversation: {result['error']}")
                    except Exception as gen_error:
                        st.error(f"Error in conversation generation: {str(gen_error)}")

        # Display conversation with enhanced UI
        if st.session_state.podcast_conversation:
            st.markdown("---")
            st.markdown("#### 🎧 Podcast Conversation")

            # Conversation metrics
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            with metrics_col1:
                num_exchanges = len(st.session_state.podcast_conversation)
                st.metric("Conversation Turns", num_exchanges)
            with metrics_col2:
                avg_response_length = sum(len(turn["content"].split())
                                          for turn in st.session_state.podcast_conversation) / num_exchanges
                st.metric("Avg Response Length", f"{int(avg_response_length)} words")
            with metrics_col3:
                duration_estimate = num_exchanges * 45  # Rough estimate: 45 seconds per exchange
                st.metric("Estimated Duration", f"{duration_estimate // 60}:{duration_estimate % 60:02d} min")
            with metrics_col4:
                st.metric("Conversation Style", style.title())

            # Export options
            st.download_button(
                label="📥 Download Script",
                data="\n\n".join([f"{'Host' if m['role'] == 'host' else 'Expert'}: {m['content']}"
                                  for m in st.session_state.podcast_conversation]),
                file_name=f"podcast_script_{style}.txt",
                mime="text/plain",
            )

            # Display conversation
            st.markdown("##### Conversation Flow")
            for turn in st.session_state.podcast_conversation:
                with st.chat_message(
                        turn["role"],
                        avatar="🎙️" if turn["role"] == "host" else "👨‍🏫"
                ):
                    # Add speaker label with styling
                    if turn["role"] == "host":
                        st.markdown("""
                            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
                                <span style='color: #ff4b4b; font-weight: bold;'>Host:</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
                                <span style='color: #4b4bff; font-weight: bold;'>Expert:</span>
                            </div>
                        """, unsafe_allow_html=True)

                    # Display content with segment indicator
                    st.markdown(f"*Segment {turn['segment']}*")
                    st.write(turn["content"])

                    # Add interaction hints for longer responses
                    if len(turn["content"].split()) > 100:
                        st.caption("💡 *Long response - contains detailed explanation*")

    except Exception as podcast_error:
        st.error(f"Error in podcast interface: {str(podcast_error)}")
        if hasattr(st.session_state.get('podcast_generator'), 'display_debug_info'):
            st.session_state.podcast_generator.display_debug_info()


def main():
    # Set page config
    st.set_page_config(
        page_title=Settings.APP_TITLE,
        page_icon="📚",
        layout="wide"
    )

    st.title(Settings.APP_TITLE)
    st.markdown("*Chat with your documents and get AI-enhanced insights* 🤖")

    # Initialize session state
    initialize_session_state()

    # Sidebar setup
    with st.sidebar:
        st.title("📁 Document Upload")
        file_type = st.selectbox(
            "Select file type:",
            ["PDF", "TXT"],
            help="Choose your document format"
        )

        allowed_types = ['pdf'] if file_type == "PDF" else ['txt']
        file = st.file_uploader(
            f"Upload your {file_type} file",
            type=allowed_types,
            help=f"Maximum file size: {Settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
        )

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        if st.button("📄 New Document", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Main content area
    if file is not None:
        # Check if it's a new document
        if st.session_state.current_doc != file.name:
            content = handle_file_upload(file, file_type)
            if content:
                # Update session state
                st.session_state.current_doc = file.name
                st.session_state.chat_engine = ChatEngine(content)
                st.session_state.document_stats = DocumentProcessor.get_document_stats(content)
                st.session_state.document_content = content

                # Reset podcast-related state
                st.session_state.podcast_conversation = None
                st.session_state.topics = None
                st.session_state.podcast_generator = None  # Force re-initialization

                display_document_stats(st.session_state.document_stats)
                st.success("✅ Document processed successfully!")

        if st.session_state.chat_engine and st.session_state.document_content:
            # Create tabs for different features
            tab1, tab2 = st.tabs(["💭 Chat", "🎙️ Podcast"])

            with tab1:
                st.markdown("### 💭 Chat with your document")
                st.markdown("*Ask questions and get insights from both the document and AI*")

                # Display chat history
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

                # Chat input
                user_input = st.chat_input("Ask your question here...")

                if user_input:
                    # Add user message
                    user_message = format_chat_message("user", user_input)
                    st.session_state.chat_history.append(user_message)

                    with st.chat_message("user"):
                        st.write(user_input)

                    # Generate response
                    with st.spinner("🤔 Generating response..."):
                        context = st.session_state.chat_engine.find_relevant_context(user_input)
                        response_data = st.session_state.chat_engine.generate_response(user_input, context)

                    if "error" not in response_data:
                        # Add assistant response
                        assistant_message = format_chat_message("assistant", response_data["combined_response"])
                        st.session_state.chat_history.append(assistant_message)

                        with st.chat_message("assistant"):
                            st.write(response_data["combined_response"])

                            col1, col2 = st.columns(2)
                            with col1:
                                with st.expander("📚 View Book's Response"):
                                    st.markdown("**From the book:**")
                                    st.write(response_data["book_response"])
                                    st.markdown("---")
                                    st.markdown("**Relevant Context:**")
                                    st.markdown(f"*{response_data['context']}*")

                            with col2:
                                with st.expander("🔍 Additional AI Insights"):
                                    st.markdown("**Enhanced understanding:**")
                                    st.write(response_data["additional_info"])
                    else:
                        st.error(f"Error generating response: {response_data['error']}")

            with tab2:
                display_podcast_interface()
    else:
        # Welcome message and feature overview
        st.info("👋 Welcome! Please upload a PDF or TXT file to start chatting!")

        # Feature overview
        st.markdown("### ✨ Features")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - 📚 **Document Analysis**
              - Text extraction and processing
              - Detailed document statistics
              - Reading time estimation

            - 💡 **Smart Responses**
              - Context-aware answers
              - Book-based information
              - AI-enhanced insights
            """)
        with col2:
            st.markdown("""
            - 🎙️ **Podcast Generation**
              - Interactive conversations
              - Multiple speaking styles
              - Topic identification
              - Downloadable scripts

            - 🤝 **User Experience**
              - Dual-mode interface
              - Easy document management
              - Clear presentation
            """)


if __name__ == "__main__":
    try:
        main()
    except Exception as main_error:
        st.error(f"An unexpected error occurred: {str(main_error)}")
        if  'debug_log' in st.session_state:
            with st.expander("🔍 Debug Information"):
                st.write(st.session_state.debug_log)