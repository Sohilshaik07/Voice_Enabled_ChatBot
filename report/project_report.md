# Voice-Enabled Chatbot Using Speech Recognition and Deep Learning

## Abstract

This project implements a university-information chatbot that accepts recorded voice, converts it to text with Google Speech Recognition, and predicts the user's intent using a TensorFlow/Keras Bidirectional LSTM (Bi-LSTM). The predicted intent selects a suitable response from a custom dataset. A text-input option supports testing when a microphone cannot be used.

## Introduction, objective, and problem statement

Students often need quick answers about admissions, courses, fees, services, and campus life. The objective is to demonstrate an online pipeline from speech to a deep-learning intent classifier and a clear chatbot response, rather than a keyword-only bot.

## Dataset description and preprocessing

`dataset/intents.json` contains 15 intents—greeting, goodbye, thanks, admission, courses, fees, faculty, library, hostel, placements, campus, timetable, examinations, contact, and scholarships—with 30 varied English patterns each (450 total). Each intent also has response alternatives. Text is lowercased, punctuation is removed, whitespace is normalized, tokenized, converted to integer sequences, and post-padded to 20 tokens. The same `normalize_text` function is used in training and inference.

Intent ownership is explicit to reduce overlap: tuition and general academic payments are `fees`; accommodation charges, rooms, mess, and residence rules are `hostel`. Class-period and lecture planning are `timetable`; exam dates, hall tickets, marks, and revaluation are `examinations`. The dataset does not use duplicate patterns as a substitute for diversity.

## Speech recognition methodology

Streamlit's `st.audio_input` records browser microphone audio. `SpeechRecognition` reads the WAV bytes and sends them to Google Speech Recognition. Unknown speech, service/network failures, invalid audio, and empty recordings return readable messages rather than crashing the interface. Internet connectivity is required for transcription.

## Deep learning model and chatbot methodology

The training script performs a stratified 80:20 train/validation split, creates a tokenizer and label encoder, then trains this model:

`Embedding(128) → SpatialDropout(0.15) → Bidirectional(LSTM(96, return_sequences=True, dropout=0.15)) → GlobalMaxPooling → Dropout(0.30) → Dense(96, ReLU, L2=0.0001) → Dropout(0.30) → Dense(15, Softmax)`.

Adam (learning rate 0.001) optimization and sparse categorical cross-entropy are used. A stratified 80:20 split is made before fitting the evaluation tokenizer, preventing validation vocabulary leakage. Early stopping monitors validation loss and restores the best weights for held-out evaluation. After metrics are recorded, a fresh final model is fitted on all labelled patterns for deployment. The saved `.keras` model, tokenizer, and label encoder are loaded by Streamlit; therefore the application does not retrain at startup. During inference, the softmax maximum gives the predicted intent and confidence. Predictions below 0.50 use a rephrase fallback instead of an arbitrary response.

## System architecture and implementation

`Voice → browser audio → Google speech-to-text → preprocessing → tokenizer/padding → Bi-LSTM → softmax intent → response`.

The implementation is organized into `app.py`, `train.py`, and reusable `src/` modules. The UI displays submitted/recognized speech, intent, confidence, response, and conversation history.

## Results

The locally executed held-out evaluation produced training accuracy **97.22%**, validation loss **1.1982**, validation accuracy **72.22%**, weighted precision **75.50%**, weighted recall **72.22%**, and weighted F1-score **72.34%**, after **21** early-stopped epochs. The best validation loss occurred at epoch **13**; loss subsequently rose while training loss continued to decline, so restored early-stopping weights are used for evaluation. The classification report is printed by `python train.py`; the full labelled confusion matrix and epoch history are saved as `model/confusion_matrix.json` and `model/training_history.json`. The final app artifact is intentionally refit on all labelled examples and should not be described as the held-out best checkpoint. `python test_chatbot.py` verifies two representative questions for every intent, plus unrelated-question fallback, empty-text, and empty-audio error handling.

## Deployment

The project targets Streamlit Community Cloud. `requirements.txt` lists runtime dependencies and all paths are project-relative. The trained artifacts must be committed to the deployment repository. The public URL should only be reported after a successful deployment.

## Limitations, future enhancements, and conclusion

The model is based on a small English demonstration dataset and cannot reliably answer open-domain questions. Speech recognition depends on Google service availability and browser microphone permission. Future versions can add labelled data, multilingual support, text-to-speech, official university data integrations, and evaluation with held-out real questions. The project nevertheless demonstrates the required end-to-end voice, speech-recognition, deep-learning intent classification, and response-generation workflow.

## References

1. TensorFlow/Keras documentation, https://www.tensorflow.org/api_docs
2. SpeechRecognition documentation, https://pypi.org/project/SpeechRecognition/
3. Streamlit documentation, https://docs.streamlit.io/
