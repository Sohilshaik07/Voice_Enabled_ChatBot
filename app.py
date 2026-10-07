"""Streamlit interface for voice-to-intent university information chatbot."""

from __future__ import annotations



import json

import uuid
from html import escape

import streamlit as st

import streamlit.components.v1 as components



from src.chatbot import load_artifacts, load_responses, reply_for

from src.speech_recognition_utils import transcribe_wav






def render_auto_tts(text: str, response_id: str, should_speak: bool = False) -> None:

    """Render browser-native Web Speech API auto-TTS for the chatbot response.



    Automatically triggers window.speechSynthesis for newly generated responses only.

    Prevents duplicate playback on page reruns or widget interactions.

    """

    if not text or not str(text).strip():

        return



    payload = json.dumps(str(text))

    escaped_id = json.dumps(str(response_id))

    should_speak_js = "true" if should_speak else "false"



    status_class = "speaking" if should_speak else "spoken"

    icon_class = "speaker-icon pulsing" if should_speak else "speaker-icon"

    label_text = "🔊 [Automatically speaking...]" if should_speak else "🔊 [Response spoken]"



    html_code = f"""

    <!DOCTYPE html>

    <html lang="en">

    <head>

      <meta charset="utf-8">

      <style>

        * {{

          box-sizing: border-box;

          margin: 0;

          padding: 0;

        }}

        body {{

          background: transparent;

          overflow: hidden;

          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

          display: flex;

          align-items: center;

          padding: 2px 0;

        }}

        .status-badge {{

          display: inline-flex;

          align-items: center;

          gap: 0.45rem;

          font-size: 0.85rem;

          font-weight: 500;

          line-height: 1.2;

          padding: 0.35rem 0.85rem;

          border-radius: 9999px;

          user-select: none;

          transition: all 0.2s ease;

        }}

        .status-badge.speaking {{

          color: #ff4b4b;

          background-color: rgba(255, 75, 75, 0.1);

          border: 1px solid rgba(255, 75, 75, 0.3);

        }}

        .status-badge.spoken {{

          color: #059669;

          background-color: rgba(5, 150, 105, 0.1);

          border: 1px solid rgba(5, 150, 105, 0.25);

        }}

        @media (prefers-color-scheme: dark) {{

          .status-badge.spoken {{

            color: #34d399;

            background-color: rgba(52, 211, 153, 0.12);

            border-color: rgba(52, 211, 153, 0.3);

          }}

          .status-badge.speaking {{

            color: #ff6b6b;

            background-color: rgba(255, 107, 107, 0.15);

            border-color: rgba(255, 107, 107, 0.35);

          }}

        }}

        .speaker-icon {{

          font-size: 0.9rem;

        }}

        @keyframes pulse {{

          0%, 100% {{ opacity: 1; transform: scale(1); }}

          50% {{ opacity: 0.55; transform: scale(1.12); }}

        }}

        .pulsing {{

          display: inline-block;

          animation: pulse 1.2s infinite ease-in-out;

        }}

      </style>

    </head>

    <body>

      <div id="tts-status" class="status-badge {status_class}">

        <span id="tts-icon" class="{icon_class}">🔊</span>

        <span id="tts-label">{label_text}</span>

      </div>



      <script>

        const messageText = {payload};

        const responseId = {escaped_id};

        const shouldSpeak = {should_speak_js};



        function getSynthesisEngine() {{

          if (typeof window !== 'undefined' && 'speechSynthesis' in window) {{

            return window.speechSynthesis;

          }}

          try {{

            if (window.parent && 'speechSynthesis' in window.parent) {{

              return window.parent.speechSynthesis;

            }}

          }} catch (e) {{}}

          return null;

        }}



        function createUtterance(text) {{

          if (typeof SpeechSynthesisUtterance !== 'undefined') {{

            return new SpeechSynthesisUtterance(text);

          }}

          try {{

            if (window.parent && window.parent.SpeechSynthesisUtterance) {{

              return new window.parent.SpeechSynthesisUtterance(text);

            }}

          }} catch (e) {{}}

          return null;

        }}



        function findBestEnglishVoice(engine) {{

          if (!engine) return null;

          const voices = engine.getVoices();

          if (!voices || voices.length === 0) return null;



          const englishVoices = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith('en'));

          if (englishVoices.length === 0) {{

            return voices.find(v => v.default) || voices[0];

          }}



          const naturalKeywords = [

            'natural', 'online', 'google', 'samantha', 'jenny', 'guy',

            'aria', 'david', 'zira', 'george', 'hazel', 'susan', 'neural'

          ];



          const naturalVoice = englishVoices.find(v => {{

            const name = (v.name || '').toLowerCase();

            return naturalKeywords.some(k => name.includes(k));

          }});

          if (naturalVoice) return naturalVoice;



          const defaultEnglish = englishVoices.find(v => v.default);

          if (defaultEnglish) return defaultEnglish;



          const standardLocale = englishVoices.find(v => {{

            const l = v.lang.toLowerCase();

            return l === 'en-us' || l === 'en-gb';

          }});

          if (standardLocale) return standardLocale;



          return englishVoices[0];

        }}



        function setBadgeSpeaking() {{

          const badge = document.getElementById('tts-status');

          const icon = document.getElementById('tts-icon');

          const label = document.getElementById('tts-label');

          if (badge && icon && label) {{

            badge.className = 'status-badge speaking';

            icon.className = 'speaker-icon pulsing';

            label.innerText = '🔊 [Automatically speaking...]';

          }}

        }}



        function setBadgeSpoken() {{

          const badge = document.getElementById('tts-status');

          const icon = document.getElementById('tts-icon');

          const label = document.getElementById('tts-label');

          if (badge && icon && label) {{

            badge.className = 'status-badge spoken';

            icon.className = 'speaker-icon';

            label.innerText = '🔊 [Response spoken]';

          }}

        }}



        function autoSpeak() {{

          const engine = getSynthesisEngine();

          if (!engine) return;



          // Check session storage to prevent repeated speech across iframe re-mounts

          let lastSpoken = null;

          try {{

            lastSpoken = window.sessionStorage.getItem('last_spoken_id');

          }} catch (e) {{}}



          if (lastSpoken === responseId || !shouldSpeak) {{

            // Already spoken or not a newly generated response

            setBadgeSpoken();

            return;

          }}



          // Record this response ID as spoken in sessionStorage

          try {{

            window.sessionStorage.setItem('last_spoken_id', responseId);

          }} catch (e) {{}}



          // 8. Cancel any currently playing speech before speaking the new response

          engine.cancel();



          // Safe check for empty text

          if (!messageText || !messageText.trim()) return;



          const utterance = createUtterance(messageText);

          if (!utterance) return;



          utterance.lang = 'en-US';

          utterance.rate = 1.0;

          utterance.pitch = 1.0;



          utterance.onstart = function() {{

            setBadgeSpeaking();

          }};

          utterance.onend = function() {{

            setBadgeSpoken();

          }};

          utterance.onerror = function() {{

            setBadgeSpoken();

          }};



          const startUtterance = () => {{

            const voice = findBestEnglishVoice(engine);

            if (voice) {{

              utterance.voice = voice;

            }}

            setBadgeSpeaking();

            engine.speak(utterance);

          }};



          const voices = engine.getVoices();

          if (voices && voices.length > 0) {{

            startUtterance();

          }} else {{

            let triggered = false;

            const triggerOnce = () => {{

              if (triggered) return;

              triggered = true;

              startUtterance();

            }};

            engine.onvoiceschanged = triggerOnce;

            setTimeout(triggerOnce, 150);

          }}

        }}



        if (document.readyState === 'loading') {{

          document.addEventListener('DOMContentLoaded', autoSpeak);

        }} else {{

          autoSpeak();

        }}

      </script>

    </body>

    </html>

    """

    components.html(html_code, height=36)






@st.cache_resource(show_spinner="Loading trained Bi-LSTM model...")
def resources():
    model, tokenizer, label_encoder = load_artifacts()
    return model, tokenizer, label_encoder, load_responses()


# ---------------------------------------------------------------------------
# Premium UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Voice AI Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ---------- Global ---------- */
    :root {
        --bg: #0b0d0f;
        --panel: #111417;
        --panel-2: #15191d;
        --border: #262c31;
        --border-soft: #1d2227;
        --text: #f4f1ea;
        --muted: #969da5;
        --accent: #e6a34a;
        --accent-soft: rgba(230, 163, 74, 0.12);
        --success: #66c28a;
        --danger: #e27d7d;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stAppViewContainer"] > .main {
        background:
            radial-gradient(circle at 78% 8%, rgba(230,163,74,.055), transparent 28%),
            var(--bg);
    }

    [data-testid="stHeader"] {
        background: rgba(11,13,15,.86);
    }

    [data-testid="stSidebar"] {
        background: #0e1113;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .block-container {
        max-width: 1420px;
        padding: 2.2rem 3rem 1.5rem;
    }

    /* ---------- Typography ---------- */
    h1, h2, h3, h4, p, label, div, span {
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    /* ---------- Header ---------- */
    .hero {
        border-bottom: 1px solid var(--border);
        padding: .35rem 0 1.8rem;
        margin-bottom: 1.5rem;
    }

    .hero-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
    }

    .eyebrow {
        color: var(--accent);
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }

    .hero-title {
        color: var(--text);
        font-size: clamp(2rem, 4vw, 3.45rem);
        font-weight: 760;
        letter-spacing: -.055em;
        line-height: 1.02;
        margin: 0;
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 1rem;
        margin: .8rem 0 0;
        max-width: 720px;
        line-height: 1.65;
    }

    .online-pill {
        display: inline-flex;
        align-items: center;
        gap: .5rem;
        border: 1px solid rgba(102,194,138,.28);
        background: rgba(102,194,138,.07);
        color: #8bd5a5;
        border-radius: 999px;
        padding: .48rem .78rem;
        white-space: nowrap;
        font-size: .78rem;
        font-weight: 700;
    }

    .online-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 0 4px rgba(102,194,138,.08);
    }

    /* ---------- Section labels ---------- */
    .section-kicker {
        color: #d4d0c7;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin: .2rem 0 .7rem;
    }

    .section-note {
        color: var(--muted);
        font-size: .86rem;
        margin: 0 0 1rem;
    }

    /* ---------- Cards ---------- */
    .ui-card {
        background: linear-gradient(145deg, #121619, #0f1215);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1.25rem;
        box-shadow: 0 16px 45px rgba(0,0,0,.18);
    }

    .voice-card {
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background:
            radial-gradient(circle at 80% 20%, rgba(230,163,74,.09), transparent 34%),
            linear-gradient(145deg, #14181b, #0f1215);
    }

    .voice-icon {
        width: 52px;
        height: 52px;
        display: grid;
        place-items: center;
        border-radius: 15px;
        background: var(--accent-soft);
        border: 1px solid rgba(230,163,74,.22);
        font-size: 1.45rem;
        margin-bottom: .85rem;
    }

    .card-title {
        color: var(--text);
        font-size: 1.15rem;
        font-weight: 760;
        margin-bottom: .25rem;
    }

    .card-copy {
        color: var(--muted);
        font-size: .88rem;
        line-height: 1.55;
    }

    /* ---------- Streamlit widgets ---------- */
    div[data-testid="stAudioInput"] {
        margin-top: .8rem;
    }

    div[data-testid="stAudioInput"] > div {
        border: 1px solid #353b41;
        border-radius: 14px;
        background: #0c0f11;
    }

    div.stButton > button {
        border-radius: 12px;
        min-height: 2.65rem;
        font-weight: 750;
        border: 1px solid #343a40;
        background: #181c20;
        color: #eeeae2;
        transition: transform .15s ease, border-color .15s ease,
                    background .15s ease;
    }

    div.stButton > button:hover {
        border-color: #666d75;
        background: #20252a;
        transform: translateY(-1px);
    }

    div.stButton > button[kind="primary"] {
        background: var(--accent);
        border-color: var(--accent);
        color: #17120b;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #f0b363;
        border-color: #f0b363;
    }

    div[data-testid="stTextInput"] input {
        background: #0e1113;
        color: var(--text);
        border: 1px solid #343a40;
        border-radius: 12px;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent);
    }

    /* ---------- Chat ---------- */
    .chat-wrap {
        background: #0e1113;
        border: 1px solid var(--border);
        border-radius: 20px;
        min-height: 430px;
        max-height: 560px;
        overflow-y: auto;
        padding: 1.25rem;
    }

    .chat-empty {
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 2rem;
    }

    .chat-empty-icon {
        font-size: 2rem;
        margin-bottom: .8rem;
    }

    .chat-empty-title {
        color: var(--text);
        font-size: 1.15rem;
        font-weight: 750;
    }

    .chat-empty-copy {
        color: var(--muted);
        max-width: 440px;
        font-size: .88rem;
        line-height: 1.6;
        margin-top: .45rem;
    }

    .message {
        display: flex;
        gap: .75rem;
        margin: .9rem 0;
        align-items: flex-start;
    }

    .message.user {
        justify-content: flex-end;
    }

    .avatar {
        flex: 0 0 34px;
        width: 34px;
        height: 34px;
        border-radius: 11px;
        display: grid;
        place-items: center;
        font-size: .9rem;
        border: 1px solid var(--border);
        background: #181c20;
    }

    .message-body {
        max-width: 78%;
    }

    .message-meta {
        color: #747c84;
        font-size: .68rem;
        font-weight: 750;
        letter-spacing: .07em;
        text-transform: uppercase;
        margin-bottom: .3rem;
    }

    .bubble {
        padding: .8rem .95rem;
        border-radius: 15px;
        font-size: .9rem;
        line-height: 1.55;
        border: 1px solid var(--border);
    }

    .bubble-user {
        background: #1a1f23;
        color: #f1eee8;
        border-top-right-radius: 5px;
    }

    .bubble-bot {
        background: #14181b;
        color: #e7e4de;
        border-top-left-radius: 5px;
    }

    .bot-response {
        color: #eeeae2;
        font-size: .96rem;
        line-height: 1.65;
    }

    /* ---------- Analysis ---------- */
    .analysis-grid {
        display: grid;
        grid-template-columns: 1.45fr .75fr .75fr;
        gap: .7rem;
        margin-top: .9rem;
    }

    .metric {
        background: #0d1012;
        border: 1px solid var(--border-soft);
        border-radius: 14px;
        padding: .85rem;
    }

    .metric-label {
        color: #777f87;
        font-size: .67rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }

    .metric-value {
        color: #eeeae3;
        font-size: .88rem;
        font-weight: 650;
        overflow-wrap: anywhere;
    }

    .confidence {
        color: var(--accent);
    }

    /* ---------- Suggestions ---------- */
    .suggestion-label {
        color: #858c93;
        font-size: .75rem;
        font-weight: 750;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin: 1.15rem 0 .55rem;
    }

    /* ---------- Sidebar ---------- */
    .side-brand {
        padding: .2rem 0 1.2rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.2rem;
    }

    .side-brand-title {
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 800;
    }

    .side-brand-copy {
        color: var(--muted);
        font-size: .76rem;
        line-height: 1.5;
        margin-top: .35rem;
    }

    .side-heading {
        color: #767e86;
        font-size: .66rem;
        font-weight: 850;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin: 1.1rem 0 .55rem;
    }

    .side-item {
        color: #c9c6bf;
        font-size: .83rem;
        padding: .35rem 0;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: .55rem;
        color: #b9b7b1;
        font-size: .78rem;
        padding: .28rem 0;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--success);
    }

    .model-badge {
        margin-top: .8rem;
        padding: .8rem;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: #111417;
    }

    .model-badge-label {
        color: #6f777f;
        font-size: .64rem;
        text-transform: uppercase;
        letter-spacing: .09em;
        font-weight: 800;
    }

    .model-badge-value {
        color: #ddd9d0;
        font-size: .82rem;
        font-weight: 700;
        margin-top: .25rem;
    }

    /* ---------- Footer ---------- */
    .footer {
        border-top: 1px solid var(--border);
        margin-top: 2rem;
        padding: 1rem 0 .3rem;
        text-align: center;
        color: #686f76;
        font-size: .72rem;
        letter-spacing: .02em;
    }

    /* ---------- Responsive ---------- */
    @media (max-width: 900px) {
        .block-container {
            padding: 1.25rem 1rem;
        }

        .hero-top {
            align-items: flex-start;
            flex-direction: column;
        }

        .analysis-grid {
            grid-template-columns: 1fr;
        }

        .message-body {
            max-width: 88%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Model / state
# ---------------------------------------------------------------------------

try:
    model, tokenizer, label_encoder, responses = resources()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []

if "last_spoken_id" not in st.session_state:
    st.session_state.last_spoken_id = None

if "pending_speech_id" not in st.session_state:
    st.session_state.pending_speech_id = None


def handle_message(text: str, source: str):
    """Run the existing chatbot pipeline without changing the ML logic."""
    cleaned = str(text).strip()
    if not cleaned:
        return

    intent, confidence, response = reply_for(
        cleaned, model, tokenizer, label_encoder, responses
    )

    response_id = f"resp_{uuid.uuid4().hex[:12]}"

    st.session_state.history.append(
        {
            "id": response_id,
            "text": cleaned,
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "source": source,
        }
    )

    # Only this newly-created response is eligible for browser TTS.
    st.session_state.pending_speech_id = response_id


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="side-brand">
            <div class="side-brand-title">🎙️ Voice AI Assistant</div>
            <div class="side-brand-copy">
                University information assistant built around speech recognition
                and deep-learning intent classification.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-heading">About</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="side-item">• Voice-enabled interaction</div>
        <div class="side-item">• Speech Recognition</div>
        <div class="side-item">• Bi-LSTM intent classification</div>
        <div class="side-item">• Natural browser voice response</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-heading">System status</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="status-item"><span class="status-dot"></span>Model loaded</div>
        <div class="status-item"><span class="status-dot"></span>Speech recognition ready</div>
        <div class="status-item"><span class="status-dot"></span>Voice response ready</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="model-badge">
            <div class="model-badge-label">Neural model</div>
            <div class="model-badge-value">Bi-LSTM · Intent Classification</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown(
    """
    <section class="hero">
        <div class="hero-top">
            <div>
                <div class="eyebrow">University Intelligence Interface</div>
                <h1 class="hero-title">Voice AI Assistant</h1>
                <p class="hero-subtitle">
                    Ask university-related questions naturally. Speak or type a
                    question and receive an intent-aware answer with an automatic
                    voice response.
                </p>
            </div>
            <div class="online-pill">
                <span class="online-dot"></span>
                AI Assistant Online
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Main workspace
# ---------------------------------------------------------------------------

left_col, right_col = st.columns([0.86, 1.35], gap="large")

with left_col:
    st.markdown('<div class="section-kicker">01 · Voice interaction</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">Your voice is the primary way to interact with the assistant.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="ui-card voice-card">
            <div>
                <div class="voice-icon">🎙️</div>
                <div class="card-title">Speak your question</div>
                <div class="card-copy">
                    Record a question, stop the recording, then send it through
                    the existing speech-recognition pipeline.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    audio = st.audio_input("Record your question")

    if audio is not None:
        st.caption("Recording ready")
        if st.button("Transcribe & Ask  →", type="primary", use_container_width=True):
            with st.spinner("Recognizing speech..."):
                text, error = transcribe_wav(audio.getvalue())

            if error:
                st.warning(error)
            elif text and text.strip():
                handle_message(text, "Voice")
                st.rerun()
            else:
                st.warning("No speech was recognized. Please try again.")

    st.markdown('<div class="section-kicker" style="margin-top:1.4rem;">Text fallback</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">Prefer typing? Use the same chatbot pipeline without a microphone.</p>',
        unsafe_allow_html=True,
    )

    with st.form("text_question", clear_on_submit=True):
        typed_text = st.text_input(
            "Your question",
            placeholder="e.g. What courses are available?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send question  →", use_container_width=True)

    if submitted:
        if typed_text.strip():
            handle_message(typed_text, "Text")
            st.rerun()
        else:
            st.warning("Please enter a question.")

    st.markdown('<div class="suggestion-label">Try asking</div>', unsafe_allow_html=True)

    suggestions = [
        ("🎓", "What courses are available?"),
        ("🏠", "Is hostel available?"),
        ("💼", "Tell me about placements"),
        ("💰", "What are the fees?"),
        ("📚", "Is there a library?"),
    ]

    for row_start in range(0, len(suggestions), 2):
        cols = st.columns(2, gap="small")
        for col, (icon, question) in zip(cols, suggestions[row_start:row_start + 2]):
            with col:
                if st.button(
                    f"{icon}  {question}",
                    key=f"suggestion_{row_start}_{question}",
                    use_container_width=True,
                ):
                    handle_message(question, "Suggestion")
                    st.rerun()


with right_col:
    st.markdown('<div class="section-kicker">02 · Conversation</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">The latest interaction remains visible with its prediction details.</p>',
        unsafe_allow_html=True,
    )

    if not st.session_state.history:
        st.markdown(
            """
            <div class="chat-wrap">
                <div class="chat-empty">
                    <div class="chat-empty-icon">◌</div>
                    <div class="chat-empty-title">Ready when you are</div>
                    <div class="chat-empty-copy">
                        Start with the microphone or type a question. The assistant
                        will recognize the request, classify its intent and answer
                        using the existing trained model.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        latest = st.session_state.history[-1]

        # Recent conversation
        # Build the complete conversation card as one HTML string.
        # The HTML is kept on single logical lines to prevent Streamlit
        # Markdown from interpreting indented tags as a code block.
        recent_items = st.session_state.history[-5:]

        chat_parts = []

        for item in recent_items:
            user_text = escape(str(item["text"]))
            bot_text = escape(str(item["response"]))
            source_label = escape(str(item["source"]))

            chat_parts.append(
                '<div class="message user">'
                '<div class="message-body">'
                f'<div class="message-meta">You · {source_label}</div>'
                f'<div class="bubble bubble-user">{user_text}</div>'
                '</div>'
                '<div class="avatar">◉</div>'
                '</div>'
                '<div class="message">'
                '<div class="avatar">✦</div>'
                '<div class="message-body">'
                '<div class="message-meta">AI Assistant</div>'
                '<div class="bubble bubble-bot">'
                f'<div class="bot-response">{bot_text}</div>'
                '</div>'
                '</div>'
                '</div>'
            )

        chat_html = '<div class="chat-wrap">' + ''.join(chat_parts) + '</div>'

        st.markdown(chat_html, unsafe_allow_html=True)

        # Latest analysis
        st.markdown(
            '<div class="section-kicker" style="margin-top:1.15rem;">03 · AI analysis</div>',
            unsafe_allow_html=True,
        )

        intent_display = latest["intent"] or "Fallback / uncertain"
        confidence_display = f'{latest["confidence"]:.1%}'
        speech_label = "Recognized speech" if latest["source"] == "Voice" else "Submitted text"

        st.markdown(
            f"""
            <div class="ui-card">
                <div class="analysis-grid">
                    <div class="metric">
                        <div class="metric-label">{speech_label}</div>
                        <div class="metric-value">“{escape(str(latest["text"]))}”</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Predicted intent</div>
                        <div class="metric-value">{escape(str(intent_display))}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value confidence">{confidence_display}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Automatic browser TTS — no manual speak button.
        should_speak = st.session_state.pending_speech_id == latest["id"]

        render_auto_tts(
            latest["response"],
            response_id=latest["id"],
            should_speak=should_speak,
        )

        if should_speak:
            st.session_state.last_spoken_id = latest["id"]
            st.session_state.pending_speech_id = None


# ---------------------------------------------------------------------------
# Full conversation history
# ---------------------------------------------------------------------------

if st.session_state.history:
    st.markdown('<div class="section-kicker" style="margin-top:1.8rem;">04 · Conversation history</div>', unsafe_allow_html=True)

    with st.expander("Open previous interactions", expanded=False):
        for item in reversed(st.session_state.history):
            st.markdown(
                f"""
                <div style="
                    border-bottom:1px solid #20252a;
                    padding: .8rem 0 1rem;
                    margin-bottom:.25rem;">
                    <div style="
                        color:#777f87;
                        font-size:.67rem;
                        font-weight:800;
                        letter-spacing:.08em;
                        text-transform:uppercase;">
                        {item["source"]} · You
                    </div>
                    <div style="color:#e5e1d9; margin:.3rem 0 .65rem;">
                        {escape(str(item["text"]))}
                    </div>
                    <div style="
                        color:#777f87;
                        font-size:.67rem;
                        font-weight:800;
                        letter-spacing:.08em;
                        text-transform:uppercase;">
                        AI Assistant
                    </div>
                    <div style="color:#c9c5bd; margin-top:.3rem; line-height:1.55;">
                        {escape(str(item["response"]))}
                    </div>
                    <div style="color:#707880; font-size:.72rem; margin-top:.45rem;">
                        Intent: {escape(str(item["intent"] or "fallback"))} ·
                        Confidence: {item["confidence"]:.1%}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


st.markdown(
    """
    <div class="footer">
        Built with Speech Recognition · Bi-LSTM Deep Learning · Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
