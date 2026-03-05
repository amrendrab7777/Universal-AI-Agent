import groq
import streamlit as st

def query_ai(messages, model="llama-3.3-70b-versatile"):
    client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
    return client.chat.completions.create(model=model, messages=messages, stream=True)