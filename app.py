import streamlit as st
import groq
from duckduckgo_search import DDGS

# --- 1. PROFESSIONAL PAGE CONFIG ---
st.set_page_config(
    page_title="Universal AI Agent",
    page_icon="🌐",
    layout="centered", # Best for mobile/tablet screens
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile Optimization
st.markdown("""
    <style>
    .stApp { max-width: 850px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; font-size: 16px; }
    /* Fix for mobile input bar */
    .stChatInput { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE API AUTHENTICATION ---
# This pulls from your Streamlit "Secrets" vault (Step 3 in previous messages)
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = groq.Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ Setup Error: 'GROQ_API_KEY' not found in Streamlit Cloud Secrets.")
    st.stop()

# --- 3. WEB SEARCH ENGINE ---
def get_web_context(query):
    """Fetches real-time info from the web to answer the question."""
    try:
        with DDGS() as ddgs:
            # We fetch the top 3 results for accuracy
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except Exception:
        return "Search currently unavailable. Responding with internal knowledge."

# --- 4. UI & CHAT LOGIC ---
st.title("🌐 Universal AI Agent")
st.caption("Blazing Fast Cloud AI • Real-time Web Search • Mobile Ready")

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Handler
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        # Step A: Perform Web Search
        with st.status("🔍 Searching the web for the latest info...", expanded=False):
            context = get_web_context(prompt)
            st.write("Synthesizing answer...")

        # Step B: Create "Super Prompt" for Llama 3
        # This tells the AI to use the web data we just found
        system_instructions = f"Using this web data: {context}\n\nAnswer the user query: {prompt}"
        
        response_placeholder = st.empty()
        full_response = ""
        
        # Step C: Stream Response from Groq Cloud
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # The professional high-speed model
                messages=[{"role": "user", "content": system_instructions}],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Groq Error: {str(e)}")

    # Save the full response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
