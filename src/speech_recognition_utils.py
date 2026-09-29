"""SpeechRecognition adapter for Streamlit audio uploads."""
from __future__ import annotations

import io
import speech_recognition as sr


def transcribe_wav(audio_bytes: bytes) -> tuple[str | None, str | None]:
    """Return (recognized_text, error_message) without letting provider errors crash the app."""
    if not audio_bytes:
        return None, "No audio was received. Please record a short question and try again."
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio), None
    except sr.UnknownValueError:
        return None, "Speech was not understood. Please speak clearly and try again."
    except sr.RequestError:
        return None, "Speech recognition is currently unavailable. Check the internet connection and try again."
    except (ValueError, OSError) as error:
        return None, f"The audio could not be processed: {error}"
