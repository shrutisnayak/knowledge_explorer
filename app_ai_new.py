import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import threading
import queue

# --- Initialization ---

# Load environment variables from a .env file
load_dotenv()

# Configure the Gemini API with the key from environment variables
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        st.error("🔴 GOOGLE_API_KEY not found. Please set it in your .env file.")
        st.stop()
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"🔴 Error configuring Gemini API: {e}")
    st.stop()

# --- Helper Function for Prompt Generation ---

def build_prompt(topic, question):
    topic_instructions = {
        "Space": "You are a witty expert on space, astronomy, and cosmology.",
        "History": "You are a knowledgeable historian who can explain events with clarity and context.",
        "Science": "You are a passionate science communicator who makes complex topics easy to understand.",
        "Technology": "You are a tech enthusiast who is up-to-date on the latest trends and gadgets.",
        "Current Events": "You are a journalist who reports on and analyzes the latest news and world events.",
        "Weather": "You are a meteorologist who can explain weather phenomena and forecasts.",
        "Literature": "You are a literary critic who can discuss authors, genres, and themes in a thoughtful way.",
        "Finance": "You are a financial advisor who can explain economic concepts and market trends.",
    }
    instruction = topic_instructions.get(topic, "You are a helpful general-purpose assistant.")
    return f"""
    **Topic:** {topic}
    **Instruction:** {instruction}
    
    Please answer the following question based on the provided topic and instruction.
    
    **Question:** {question}
    """

# --- Main Streamlit Application ---

def main():
    st.set_page_config(
        page_title="Knowledge Explorer AI 🤖",
        page_icon="🤖",
        layout="wide"
    )

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Response Settings")
        new_topics = ["General", "Space", "History", "Science", "Technology", "Current Events", "Weather", "Literature", "Finance"]
        sorted_items = sorted(new_topics)
        selected_topic = st.selectbox("Choose a topic:", sorted_items, index=2, label_visibility="collapsed")

        st.markdown("---")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
        top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.05)
        top_k = st.slider("Top K", 1, 50, 40, 1)
        generation_config = {"temperature": temperature, "top_p": top_p, "top_k": top_k}

        st.markdown("---")
        st.subheader("💬 Conversation")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat = None
            st.rerun()

    # Session State Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat" not in st.session_state or st.session_state.chat is None:
        try:
            model = genai.GenerativeModel(model_name='gemini-2.5-flash')
            st.session_state.chat = model.start_chat(history=[])
        except Exception as e:
            st.error(f"🔴 Failed to initialize Gemini model: {e}")
            st.stop()

    # Main Chat Interface
    st.title("✨ Knowledge Explorer AI")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about " + selected_topic + "...",
                               key="main_chat_input",
                               max_chars=None,
                               accept_file=True,
                               file_type=["jpg", "jpeg", "png", "pdf", "webp"],
                               disabled=False):

        # Display user message
        user_content = prompt.text

        if prompt.files:
            file_list_md = "\n".join([f"- 📎 {file.name}" for file in prompt.files])
            user_content += f"\n\n**Uploaded file(s):**\n{file_list_md}"

        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_content})
        with st.chat_message("user"):
            st.markdown(prompt.text)
            
            # Optionally preview images directly
            for file in prompt.files:
                if file.type.startswith("image/"):
                    st.image(file, caption=file.name, width=100)

                # Assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            typing_placeholder = st.empty()
            time_placeholder = st.empty()
            full_response = ""

            q = queue.Queue()
            chat = st.session_state.chat  # copy chat reference outside thread

            # Worker: Gemini streaming
            def stream_worker():
                try:
                    contextual_prompt = build_prompt(selected_topic, prompt.text)
                    file_inputs = []
                    if prompt.files:
                        for file in prompt.files:
                            temp_path = os.path.join("temp", file.name)
                            os.makedirs("temp", exist_ok=True)
                            with open(temp_path, "wb") as f:
                                f.write(file.getbuffer())
                            gemini_file = genai.upload_file(temp_path)
                            file_inputs.append(gemini_file)
                        contextual_prompt = [contextual_prompt] + file_inputs

                    for chunk in chat.send_message(
                        contextual_prompt,
                        generation_config=generation_config,
                        stream=True
                    ):
                        text = getattr(chunk, "text", None)
                        if text:
                            q.put(("chunk", text))
                except Exception as e:
                    q.put(("error", str(e)))
                finally:
                    q.put(("done", None))

            worker_thread = threading.Thread(target=stream_worker, daemon=True)
            worker_thread.start()

            start_time = time.time()
            dots = ["", ".", "..", "..."]
            dot_index = 0
            first_chunk_received = False
            finished = False
            queue_poll_timeout = 0.25

            try:
                while not finished:
                    try:
                        kind, payload = q.get(timeout=queue_poll_timeout)
                    except queue.Empty:
                        if not first_chunk_received:
                            typing_placeholder.markdown(f"🤖 Thinking{dots[dot_index % 4]}")
                            dot_index += 1
                        continue

                    if kind == "chunk":
                        if not first_chunk_received:
                            first_chunk_received = True
                            typing_placeholder.empty()

                        # Just append chunk directly (no char-by-char typing)
                        full_response += payload
                        message_placeholder.markdown(full_response + "▌")

                    elif kind == "error":
                        typing_placeholder.empty()
                        message_placeholder.error("An error occurred: " + payload)
                        finished = True

                    elif kind == "done":
                        finished = True

                # Finalize response
                message_placeholder.markdown(full_response)
                end_time = time.time()
                response_time = end_time - start_time
                time_placeholder.markdown(f"⏱️ *Response time: {response_time:.2f} seconds*")

            except Exception as e:
                typing_placeholder.empty()
                message_placeholder.error(f"An unexpected error occurred: {e}")

        # Save response in history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
