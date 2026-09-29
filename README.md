# Voice-Enabled Chatbot Using Speech Recognition and Deep Learning

An assessment-ready Streamlit application that accepts recorded speech, transcribes it with Google Speech Recognition, and classifies the question with a trained TensorFlow/Keras Bi-LSTM intent model. It provides university-information responses and a text input fallback for reliable demonstrations.

## Features

- Voice recording through Streamlit's browser microphone control
- Google Speech Recognition via `SpeechRecognition`, with friendly error handling
- Custom dataset: 15 university intents × 30 varied utterances (450 examples)
- Genuine neural intent classifier: Embedding → Bidirectional LSTM → max pooling → Dense/ReLU → Softmax
- Saved model, tokenizer, and label encoder; no retraining during app startup
- Confidence threshold with a safe fallback response
- Text testing option and conversation history

Intent boundaries are deliberately defined: `fees` covers general tuition, payment, and academic charges, while accommodation-specific charges and room questions belong to `hostel`. Class schedules are `timetable`; exam dates, hall tickets, results, and revaluation are `examinations`.

## Architecture

`Voice → Speech-to-Text → normalization → tokenizer/padding → Embedding → Bi-LSTM → Softmax intent → response`

## Setup and local use

Use Python 3.10–3.12 (TensorFlow support is not currently available for Python 3.14).

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python train.py
streamlit run app.py
```

Then open the local URL shown by Streamlit and allow microphone access. Speech transcription uses Google's online service, so internet access is required for voice input. The text option lets an evaluator test the saved ML model if the browser microphone is unavailable.

## Training and evaluation

`python train.py` evaluates a validation split, then fits the final deployable model on all labelled patterns and creates these artifacts:

- `model/chatbot_model.keras`
- `model/tokenizer.pkl`
- `model/label_encoder.pkl`
- `model/training_metrics.json` (actual validation metrics)
- `model/confusion_matrix.json` (held-out evaluation confusion matrix)
- `model/training_history.json` (per-epoch training and validation curves)

Run `python test_chatbot.py` after training. It checks two representative utterances for every intent (30 intent checks), plus unrelated input, empty text, and empty-audio error handling. Training prints a classification report and confusion matrix; do not replace those generated results with claims made in advance.

The locally generated held-out evaluation uses a stratified 80:20 split, with the evaluation tokenizer fitted only on the training split. The final result is **72.22% accuracy**, **1.1982 loss**, **0.7550 weighted precision**, **0.7222 weighted recall**, and **0.7234 weighted F1**, after 21 early-stopped epochs. The best validation-loss checkpoint is epoch 13; `training_history.json` preserves the curve. The final saved model is then intentionally fitted on all 450 labelled examples for the demonstration application. This remains a compact educational dataset rather than a production benchmark.

## Deployment: GitHub and Streamlit Community Cloud

1. Train locally and verify `python test_chatbot.py`.
2. Commit the three trained artifacts in `model/` so Community Cloud can load them. Do not commit virtual environments or secrets.
3. Create a GitHub repository, then run:

```bash
git init
git add .
git commit -m "Build voice-enabled Bi-LSTM chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

4. At [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, select the repository/`main` branch, set the main file to `app.py`, and deploy.
5. Add the resulting URL here after it is verified: **Deployed URL: _not deployed yet_**.

Community Cloud provides HTTPS, so browsers can request microphone permission. It must be granted by the user. No secret keys are stored in this project.

## Limitations and future work

This small, curated English dataset is intended for demonstration rather than open-domain support. Google recognition needs network connectivity. Production improvements include more labelled utterances, monitored evaluation data, multilingual models, database-backed current university information, and authenticated official APIs.
