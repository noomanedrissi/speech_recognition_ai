# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 21:32:54 2026

@author: noomane.drissi
"""

import streamlit as st
from groq import Groq

st.set_page_config(page_title="ND AI Tutor", page_icon="🤖", layout="wide")

# Secure API Key handling
try:
    client = Groq(api_key="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")
except Exception:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VOICE TRANSCRIPTION FUNCTION ---
def transcribe_audio(audio_data):
    # Transcription happens instantly on Groq's infrastructure
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_data.read()),
        model="whisper-large-v3-turbo", 
        response_format="text"
    )
    return transcription

# Sidebar logic
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- UNIFIED INPUT (TEXT + VOICE) ---
# Setting accept_audio=True adds a microphone icon to the chat input bar
prompt = st.chat_input("Type your question or click the mic to speak...", accept_audio=True)

if prompt:
    user_text = ""

    # Check if the user used the microphone or typed text
    if hasattr(prompt, 'audio') and prompt.audio is not None:
        with st.spinner("Transcribing your voice..."):
            user_text = transcribe_audio(prompt.audio)
    else:
        user_text = prompt if isinstance(prompt, str) else prompt.get("text", "")

    if user_text:
        # Add to history and display
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.chat_message("user").write(user_text)
        
        # Generate AI Tutor response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                messages_with_history = [{"role": "system", "content": "You are a helpful AI assistant"}] + st.session_state.messages
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_with_history
                )
                full_response = response.choices[0].message.content
                st.write(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})