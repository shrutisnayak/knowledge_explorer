import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("Please set your GOOGLE_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.5-flash')

def get_ai_response(question, topic):
    if topic == "Space":
        question_prompt = f"""
        You are a Space expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "History":
        question_prompt = f"""
        You are an historian that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Science":
        question_prompt = f"""
        You are a Science expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Technology":
        question_prompt = f"""
        You are a Technology expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Current Events":
        question_prompt = f"""
        You are a Current Events expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Weather":
        question_prompt = f"""
        You are a Weather expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Literature":
        question_prompt = f"""
        You are a Literature expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Finance":
        question_prompt = f"""
        You are a Finance expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    else:
        question_prompt = f"""
        You are a helpful assistant that can answer questions about the topic: {topic}.
        Question: {question}
        """

    response = model.generate_content(question_prompt)
    return response.text

def get_ai_response_with_file(question, files, topic):
    if topic == "Space":
        question_prompt = f"""
        You are a Space expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "History":
        question_prompt = f"""
        You are an historian that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Science":
        question_prompt = f"""
        You are a Science expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Technology":
        question_prompt = f"""
        You are a Technology expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Current Events":
        question_prompt = f"""
        You are a Current Events expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Weather":
        question_prompt = f"""
        You are a Weather expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Literature":
        question_prompt = f"""
        You are a Literature expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    elif topic == "Finance":
        question_prompt = f"""
        You are a Finance expert that can answer questions about the topic: {topic}.
        Question: {question}
        """
    else:
        question_prompt = f"""
        You are a helpful assistant that can answer questions about the topic: {topic}.
        Question: {question}
        """

    # Ensure SDK supports file uploads
    if not hasattr(genai, "upload_file"):
        st.error("Your google-generativeai package is too old for file uploads. Please upgrade to version 0.8.0 or newer.")
        return "Upgrade google-generativeai to >=0.8.0 to enable PDF/image uploads."

    # Upload files (images/PDFs) to Gemini and wait until they are ACTIVE
    gemini_files = []
    for f in files:
        # Persist the UploadedFile to disk so the SDK can upload it by path
        suffix = os.path.splitext(f.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(f.getbuffer())
            tmp_path = tmp.name

        try:
            uploaded = genai.upload_file(path=tmp_path, mime_type=f.type if hasattr(f, 'type') else None)
            gemini_files.append(uploaded)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    # Optionally wait until files are processed
    for gf in gemini_files:
        try:
            while True:
                status = genai.get_file(gf.name)
                state = getattr(status, 'state', None)
                state_name = getattr(state, 'name', None)
                if state_name == 'PROCESSING':
                    time.sleep(0.2)
                    continue
                break
        except Exception:
            break

    response = model.generate_content([*gemini_files, question_prompt])
    return response.text


def preview_image():
    with st.spinner("🤔 Thinking ..."):
                uploaded_files = st.session_state.get("user_files", [])

                if uploaded_files:
                    for file in uploaded_files:
                        if file.type.startswith('image/'):
                            st.image(file, caption="Preview ...", use_container_width=False, width=250)


def main():
    st.set_page_config(
        page_title="Knowledge Explorer AI",
        page_icon="🤖",
        layout="wide"
    )

    with st.sidebar:
            st.title("About me!")
            st.markdown("""
            - **Curiosity Has No Limits:** Wondering about something? Anything at all? Our agent is here to provide answers.
            - **Diverse Topics Welcome:** Feel free to ask about anything – history, science, technology, current events, or even just a quick question about the weather.
            - **One Source for All Your Questions:** Streamline your search for information with our versatile agent.
            """)

            st.markdown("Go ahead, try it out!")

    col1, col2 = st.columns([3,1])

    with col1:
        st.write("### Explore to the new world of knowledge! ✨")

        st.markdown("<b>📖 Select a Topic!</b>", unsafe_allow_html=True)

        sorted_items=sorted(["General", "Space", "History", "Science", "Technology", "Current Events", "Weather","Literature","Finance"])

        selected_topic = st.selectbox("", sorted_items, index=2, label_visibility="collapsed")

        col3, col4 = st.columns([1, 1])

        with col3:
            st.markdown("<b style='font-size: 12px;'>📂 You may upload files to help the AI answer your question better!</b>", unsafe_allow_html=True)
            # File uploader
            user_files = st.file_uploader("",type=["jpg","jpeg","png","pdf"], 
            on_change=preview_image, label_visibility="collapsed", accept_multiple_files=True, key="user_files")

        with col4:
            st.markdown("<b style='font-size: 13px;'>💡 Try Asking:</b>", unsafe_allow_html=True)
            # Input area
            user_question = st.text_input(
                "",
                placeholder="e.g., Explain the concept of quantum mechanics",
                key="user_input",
                label_visibility="collapsed"
                )
            
        # Ask button
        if st.button("👉 Ask AI", type="primary", use_container_width=True):
                if user_files and user_question:
                    with st.spinner("🤔 Thinking ..."):
                            response = get_ai_response_with_file(user_question, user_files, selected_topic)
                            st.markdown("### 🤓☝️ AI Response:")
                            st.markdown(response)
                elif user_question:
                    with st.spinner("🤔 Thinking ..."):
                            response = get_ai_response(user_question, selected_topic)
                            st.markdown("### 🤓☝️ AI Response:")
                            st.markdown(response)
                else:
                    st.warning("Please enter a question!")
    
    with col2:
        st.markdown("")

if __name__ == "__main__":
    main() 