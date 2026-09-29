"""Streamlit interface for voice-to-intent university information chatbot."""
from __future__ import annotations

import streamlit as st

from src.chatbot import load_artifacts, load_responses, reply_for
from src.speech_recognition_utils import transcribe_wav

st.set_page_config(page_title="Voice-Enabled AI Chatbot", page_icon="🎙️", layout="centered")

@st.cache_resource(show_spinner="Loading trained Bi-LSTM model...")
def resources():
    model, tokenizer, label_encoder = load_artifacts()
    return model, tokenizer, label_encoder, load_responses()

st.title("🎙️ Voice-Enabled AI Chatbot")
st.caption("University information assistant • Speech Recognition + Bi-LSTM intent classification")
st.info("Flow: Voice → Speech-to-Text → Text preprocessing → Tokenizer → Embedding → Bi-LSTM → Intent → Response")

try:
    model, tokenizer, label_encoder, responses = resources()
except FileNotFoundError as error:
    st.error(str(error)); st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

def handle_message(text: str, source: str):
    intent, confidence, response = reply_for(text, model, tokenizer, label_encoder, responses)
    st.session_state.history.append({"text": text, "intent": intent, "confidence": confidence, "response": response, "source": source})

left_col, right_col = st.columns([1, 1.2], gap="large")

with left_col:
    with st.container(border=True):
        st.subheader("🎤 Voice Input")
        st.caption("Ask your university-related question")
        audio = st.audio_input("Record your question, then stop recording.")
        if audio is not None and st.button("Transcribe and ask", type="primary", use_container_width=True):
            with st.spinner("Recognizing speech with Google Speech Recognition..."):
                text, error = transcribe_wav(audio.getvalue())
            if error:
                st.warning(error)
            else:
                handle_message(text, "Voice")

        st.divider()
        st.subheader("Text fallback")
        with st.form("text_question", clear_on_submit=True):
            typed_text = st.text_input(
                "Type a question if microphone access is unavailable",
                placeholder="e.g., What courses are available?",
            )
            submitted = st.form_submit_button("Ask chatbot", use_container_width=True)
        if submitted:
            if typed_text.strip():
                handle_message(typed_text, "Text")
            else:
                st.warning("Please enter a question.")

with right_col:
    with st.container(border=True):
        st.subheader("📊 Latest Result")
        if st.session_state.history:
            latest = st.session_state.history[-1]
            st.markdown("**Recognized / submitted text**")
            st.write(latest["text"])
            st.markdown("**Predicted intent**")
            st.code(latest["intent"] or "Fallback (uncertain)", language=None)
            st.markdown("**Confidence**")
            st.write(f"{latest['confidence']:.1%}")
            st.markdown("**🤖 Chatbot Response**")
            st.success(latest["response"])
        else:
            st.info("Your latest answer will appear here after you ask a question.")

if st.session_state.history:
    st.divider()
    st.subheader("Conversation History")
    with st.expander("Show conversation history"):
        for item in reversed(st.session_state.history):
            st.markdown(f"**{item['source']} — You:** {item['text']}  ")
            st.markdown(f"**Bot:** {item['response']} *(intent: {item['intent'] or 'fallback'}, confidence: {item['confidence']:.1%})*")
