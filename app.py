import streamlit as st
import llm_logic
import tools
import artist

st.set_page_config(page_title="Albert 2026", layout="wide")
if "messages" not in st.session_state: st.session_state.messages = []

# Sidebar for files
with st.sidebar:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Albert..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # Image Branch
        if any(w in prompt.lower() for w in ["draw", "paint", "generate"]):
            with st.spinner("🎨 Albert is painting..."):
                img = artist.create_art(prompt)
                if img: st.image(img, caption=prompt)
                else: st.error("Failed to generate.")
        
        # Research & Chat Branch
        else:
            file_txt = tools.extract_text(uploaded_file) if uploaded_file else ""
            web_ctx = tools.web_search(prompt)
            full_prompt = f"File: {file_txt}\nWeb Context: {web_ctx}\nQ: {prompt}"
            
            resp_placeholder = st.empty()
            full_resp = ""
            stream = llm_logic.query_ai([{"role": "user", "content": full_prompt}])
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_placeholder.markdown(full_resp + "▌")
            resp_placeholder.markdown(full_resp)
            st.session_state.messages.append({"role": "assistant", "content": full_resp})