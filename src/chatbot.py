"""Inference helpers for the trained intent-classification model."""
from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from src.preprocessing import MAX_SEQUENCE_LENGTH, normalize_text

FALLBACK_RESPONSE = "I'm sorry, I didn't quite understand that. Could you please rephrase your question?"
STOP_WORDS = {
    "a", "an", "and", "are", "about", "can", "could", "do", "does", "for", "how", "i", "is", "me", "my",
    "of", "on", "please", "the", "to", "what", "when", "where", "who", "will", "with", "you", "your",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_responses(dataset_path: Path | None = None) -> dict[str, list[str]]:
    dataset_path = dataset_path or project_root() / "dataset" / "intents.json"
    with open(dataset_path, encoding="utf-8") as handle:
        return {item["intent"]: item["responses"] for item in json.load(handle)["intents"]}


def load_artifacts(model_dir: Path | None = None):
    model_dir = model_dir or project_root() / "model"
    required = [model_dir / "chatbot_model.keras", model_dir / "tokenizer.pkl", model_dir / "label_encoder.pkl"]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing trained artifact(s): " + ", ".join(missing) + ". Run: python train.py")
    return load_model(required[0]), joblib.load(required[1]), joblib.load(required[2])


def predict_intent(text: str, model, tokenizer, label_encoder, threshold: float = 0.50) -> tuple[str | None, float]:
    cleaned = normalize_text(text)
    if not cleaned:
        return None, 0.0
    sequence = tokenizer.texts_to_sequences([cleaned])
    # A closed-set softmax can be overconfident on completely unrelated text.
    # Treat inputs made mostly of out-of-vocabulary words as out of scope.
    oov_index = tokenizer.word_index.get(tokenizer.oov_token)
    tokens = sequence[0]
    if not tokens or (oov_index and sum(token == oov_index for token in tokens) / len(tokens) >= 0.40):
        return None, 0.0
    # Do not send an obviously out-of-domain request to a closed-set softmax.
    # Common function words such as "what is the" should not make an unrelated
    # question appear to be university information.
    content_words = [word for word in cleaned.split() if word not in STOP_WORDS]
    known_content = [word for word in content_words if tokenizer.word_index.get(word) not in (None, oov_index)]
    if content_words and len(known_content) / len(content_words) <= 0.50:
        return None, 0.0
    padded = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    probabilities = model.predict(padded, verbose=0)[0]
    index = int(np.argmax(probabilities))
    confidence = float(probabilities[index])
    if confidence < threshold:
        return None, confidence
    return str(label_encoder.inverse_transform([index])[0]), confidence


def reply_for(text: str, model, tokenizer, label_encoder, responses: dict[str, list[str]], threshold: float = 0.50):
    intent, confidence = predict_intent(text, model, tokenizer, label_encoder, threshold)
    response = random.choice(responses[intent]) if intent else FALLBACK_RESPONSE
    return intent, confidence, response
