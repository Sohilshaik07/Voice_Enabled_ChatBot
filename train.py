"""Train and save a genuine Bi-LSTM intent classifier."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import joblib
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Bidirectional, Dense, Dropout, Embedding, GlobalMaxPooling1D, LSTM, SpatialDropout1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from src.preprocessing import MAX_SEQUENCE_LENGTH, normalize_text

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "dataset" / "intents.json"
MODEL_DIR = ROOT / "model"
SEED = 42


def load_training_data():
    with open(DATASET, encoding="utf-8") as handle:
        intents = json.load(handle)["intents"]
    texts, labels = [], []
    for item in intents:
        for pattern in item["patterns"]:
            texts.append(normalize_text(pattern))
            labels.append(item["intent"])
    return texts, labels


def build_model(vocabulary_size: int, classes: int) -> Sequential:
    model = Sequential([
        Embedding(vocabulary_size, 128, input_length=MAX_SEQUENCE_LENGTH),
        SpatialDropout1D(0.15),
        # Max pooling retains useful intent-bearing features while the Bi-LSTM
        # learns their context in both directions.
        Bidirectional(LSTM(96, return_sequences=True, dropout=0.15)),
        GlobalMaxPooling1D(),
        Dropout(0.30),
        Dense(96, activation="relu", kernel_regularizer=l2(1e-4)),
        Dropout(0.30),
        Dense(classes, activation="softmax"),
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def main():
    random.seed(SEED); np.random.seed(SEED); tf.random.set_seed(SEED)
    texts, labels = load_training_data()
    encoder = LabelEncoder()
    encoded_labels = encoder.fit_transform(labels)
    if "--deployment-only" in sys.argv:
        metrics_path = MODEL_DIR / "training_metrics.json"
        if not metrics_path.exists():
            raise FileNotFoundError("Run held-out evaluation before --deployment-only.")
        tokenizer = Tokenizer(oov_token="<OOV>")
        tokenizer.fit_on_texts(texts)
        sequences = pad_sequences(tokenizer.texts_to_sequences(texts), maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
        deployment_model = build_model(len(tokenizer.word_index) + 1, len(encoder.classes_))
        # This is an intentional final refit on all labelled data, separate
        # from the held-out checkpoint used for reporting validation metrics.
        deployment_model.fit(sequences, encoded_labels, epochs=150, batch_size=48, verbose=0)
        MODEL_DIR.mkdir(exist_ok=True)
        deployment_model.save(MODEL_DIR / "chatbot_model.keras")
        joblib.dump(tokenizer, MODEL_DIR / "tokenizer.pkl")
        joblib.dump(encoder, MODEL_DIR / "label_encoder.pkl")
        print("Saved full-dataset deployment model and preprocessing artifacts in model/.")
        return
    train_texts, val_texts, y_train, y_val = train_test_split(texts, encoded_labels, test_size=0.20, random_state=SEED, stratify=encoded_labels)
    # Fit vocabulary only on training text. This prevents even unsupervised
    # validation-vocabulary leakage during evaluation.
    evaluation_tokenizer = Tokenizer(oov_token="<OOV>")
    evaluation_tokenizer.fit_on_texts(train_texts)
    x_train = pad_sequences(evaluation_tokenizer.texts_to_sequences(train_texts), maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    x_val = pad_sequences(evaluation_tokenizer.texts_to_sequences(val_texts), maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    model = build_model(len(evaluation_tokenizer.word_index) + 1, len(encoder.classes_))
    callbacks = [EarlyStopping(monitor="val_loss", patience=8, min_delta=0.002, restore_best_weights=True)]
    history = model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=120, batch_size=24, callbacks=callbacks, verbose=2)
    train_loss, train_accuracy = model.evaluate(x_train, y_train, verbose=0)
    loss, accuracy = model.evaluate(x_val, y_val, verbose=0)
    predictions = model.predict(x_val, verbose=0).argmax(axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(y_val, predictions, average="weighted", zero_division=0)
    best_loss_epoch = int(np.argmin(history.history["val_loss"])) + 1
    best_validation_loss = float(np.min(history.history["val_loss"]))
    best_validation_accuracy = float(np.max(history.history["val_accuracy"]))
    print(f"Training loss: {train_loss:.4f}")
    print(f"Training accuracy: {train_accuracy:.4f}")
    print(f"Validation loss: {loss:.4f}")
    print(f"Validation accuracy: {accuracy:.4f}")
    print(f"Validation weighted precision: {precision:.4f}")
    print(f"Validation weighted recall: {recall:.4f}")
    print(f"Validation weighted F1: {f1:.4f}")
    print(classification_report(y_val, predictions, target_names=encoder.classes_, zero_division=0))
    matrix = confusion_matrix(y_val, predictions)
    print("Confusion matrix:\n", matrix)
    metrics = {
        "dataset_samples": len(texts), "intent_classes": len(encoder.classes_), "samples_per_intent": len(texts) // len(encoder.classes_),
        "training_loss": float(train_loss), "training_accuracy": float(train_accuracy),
        "validation_loss": float(loss), "validation_accuracy": float(accuracy),
        "validation_weighted_precision": float(precision), "validation_weighted_recall": float(recall), "validation_weighted_f1": float(f1),
        "epochs_completed": len(history.history["loss"]), "best_validation_loss": best_validation_loss,
        "best_validation_loss_epoch": best_loss_epoch, "best_validation_accuracy": best_validation_accuracy,
        "split": "stratified 80:20; tokenizer fit on training split only",
    }
    MODEL_DIR.mkdir(exist_ok=True)
    (MODEL_DIR / "training_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (MODEL_DIR / "confusion_matrix.json").write_text(
        json.dumps({"labels": encoder.classes_.tolist(), "matrix": matrix.tolist()}, indent=2), encoding="utf-8"
    )
    (MODEL_DIR / "training_history.json").write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    if "--evaluation-only" in sys.argv:
        print("Saved held-out evaluation metrics in model/training_metrics.json.")
        return
    # The validation model above is used only for an honest held-out evaluation.
    # After that evaluation, fit a fresh deployable model on every labelled
    # example so the small educational dataset is fully available to the app.
    tokenizer = Tokenizer(oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = pad_sequences(tokenizer.texts_to_sequences(texts), maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    deployment_model = build_model(len(tokenizer.word_index) + 1, len(encoder.classes_))
    # The final model is trained longer on the complete labelled corpus after
    # the held-out metrics have already been calculated. This does not affect
    # the reported evaluation and gives the deployed model enough updates to
    # learn all available labelled language patterns.
    # Intentional final refit on all labelled data for the deployed app. Its
    # held-out quality is represented by the evaluation model above, not by
    # this full-data fit, which has no validation split.
    deployment_model.fit(sequences, encoded_labels, epochs=150, batch_size=48, verbose=0)
    MODEL_DIR.mkdir(exist_ok=True)
    deployment_model.save(MODEL_DIR / "chatbot_model.keras")
    joblib.dump(tokenizer, MODEL_DIR / "tokenizer.pkl")
    joblib.dump(encoder, MODEL_DIR / "label_encoder.pkl")
    print("Saved full-dataset deployment model and preprocessing artifacts in model/.")


if __name__ == "__main__":
    main()
