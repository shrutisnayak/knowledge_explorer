import streamlit as st
import google.generativeai as genai
import os
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

# Space-related keywords to filter questions
SPACE_KEYWORDS = [
    'space', 'astronomy', 'cosmos', 'universe', 'galaxy', 'galaxies', 'star', 'stars',
    'planet', 'planets', 'solar system', 'moon', 'mars', 'venus', 'jupiter', 'saturn',
    'neptune', 'uranus', 'mercury', 'pluto', 'asteroid', 'comet', 'meteor', 'nebula',
    'black hole', 'wormhole', 'dark matter', 'dark energy', 'cosmic', 'stellar',
    'interstellar', 'extraterrestrial', 'alien', 'ufo', 'nasa', 'esa', 'spacex',
    'rocket', 'satellite', 'space station', 'iss', 'hubble', 'james webb',
    'telescope', 'constellation', 'zodiac', 'astronaut', 'cosmonaut', 'orbit',
    'gravity', 'einstein', 'relativity', 'big bang', 'expansion', 'redshift',
    'light year', 'parsec', 'quasar', 'pulsar', 'supernova', 'nova'
]

def is_space_related(question):
    """Check if the question is space-related"""
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in SPACE_KEYWORDS)

def get_gemini_response(question):
    """Get response from Gemini AI"""
    try:
        # Create a space-focused prompt
        space_prompt = f"""
        You are a space and astronomy expert. Answer the following question about space, astronomy, or related topics.
        If the question is not space-related, politely redirect the user to ask space-related questions only.
        
        Question: {question}
        
        Please provide a comprehensive, accurate, and engaging answer about space topics.
        """
        
        response = model.generate_content(space_prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Space Explorer AI",
        page_icon="🚀",
        layout="wide"
    )
    
    # Header
    st.title("🚀 Space Explorer AI")
    st.markdown("### Your AI companion for all things space and astronomy!")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This AI assistant specializes in space-related questions only. 
        Ask me about:
        - Planets and solar systems
        - Stars and galaxies
        - Space exploration
        - Astronomy discoveries
        - And much more!
        """)
        
        st.header("Instructions")
        st.markdown("""
        1. Type your space-related question
        2. Click 'Ask AI' or press Enter
        3. Get detailed answers from Gemini AI
        """)
        
        st.header("Note")
        st.markdown("""
        This AI will only answer space-related questions. 
        For other topics, please use a different AI assistant.
        """)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Input area
        user_question = st.text_input(
            "Ask me anything about space! 🌌",
            placeholder="e.g., What is a black hole? How do stars form?",
            key="user_input"
        )
        
        # Ask button
        if st.button("🚀 Ask AI", type="primary", use_container_width=True):
            if user_question.strip():
                # Check if question is space-related
                if is_space_related(user_question):
                    with st.spinner("🤖 Thinking about space..."):
                        response = get_gemini_response(user_question)
                    
                    # Display response
                    st.markdown("### 🤖 AI Response:")
                    st.markdown(response)
                    
                    # Add some space facts
                    st.markdown("---")
                    st.markdown("### 🌟 Did You Know?")
                    st.info("The universe is expanding at an accelerating rate, and we're still discovering new galaxies every day!")
                else:
                    st.warning("🚫 This question doesn't seem to be space-related. Please ask me about space, astronomy, planets, stars, galaxies, or other cosmic topics!")
            else:
                st.warning("Please enter a question!")
    
    with col2:
        # Space facts widget
        st.markdown("### 🌌 Space Facts")
        st.markdown("""
        - **Nearest Star**: Proxima Centauri (4.24 light-years)
        - **Largest Planet**: Jupiter
        - **Speed of Light**: 299,792 km/s
        - **Age of Universe**: ~13.8 billion years
        """)
        
        # Quick questions suggestions
        st.markdown("### 💡 Try Asking:")
        st.markdown("""
        - What is dark matter?
        - How do planets form?
        - What causes auroras?
        - How big is the universe?
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Powered by **Google Gemini AI** | Built with **Streamlit** | "
        "Specialized in **Space & Astronomy** 🚀"
    )

if __name__ == "__main__":
    main() 