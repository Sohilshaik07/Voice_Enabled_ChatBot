# 🎙️ Voice-Enabled Chatbot Using Speech Recognition and Deep Learning

An assessment-ready **Voice-Enabled University Chatbot** built using **Speech Recognition, TensorFlow/Keras, Bi-LSTM Deep Learning, and Streamlit**.

The application accepts spoken questions through a browser microphone, converts speech into text using Google Speech Recognition, classifies the question using a trained Bi-LSTM intent classification model, and generates an appropriate university-related response. The chatbot also supports text input as a fallback and automatically speaks the generated response using browser-native Text-to-Speech.

---

## 🚀 Live Application

**Deployed URL:** _Add your Streamlit Community Cloud URL here after deployment_

---

## ✨ Features

- 🎙️ Voice input through the browser microphone
- 🗣️ Speech-to-text using Google Speech Recognition
- 🤖 Bi-LSTM based deep-learning intent classifier
- 🧠 15 university-related intents
- 📚 450 labelled utterances
- 💬 Automatic chatbot response generation
- 🔊 Automatic browser-based Text-to-Speech response
- ⌨️ Text input fallback
- 📊 Intent confidence display
- 🛡️ Confidence-based fallback for uncertain questions
- 💾 Saved TensorFlow/Keras model and preprocessing artifacts
- 📜 Conversation history
- 🌐 Streamlit Community Cloud deployment
- ❌ No retraining required when starting the application

---

## 🎯 Supported Intents

The chatbot currently supports 15 university-related intents:

| Intent | Description |
|---|---|
| `greeting` | General greetings |
| `goodbye` | Ending the conversation |
| `thanks` | Thank-you messages |
| `admission` | Admission and application queries |
| `courses` | Courses and programmes |
| `fees` | Tuition fees and academic charges |
| `faculty` | Faculty-related questions |
| `library` | Library services |
| `hostel` | Hostel and accommodation |
| `placements` | Placements and career support |
| `campus` | Campus facilities |
| `timetable` | Class schedules and timetables |
| `examinations` | Exams, hall tickets, and results |
| `contact` | University contact information |
| `scholarships` | Scholarship-related queries |

### Intent boundaries

The intent categories are deliberately separated to reduce ambiguity:

- `fees` → general tuition, payment, and academic charges
- `hostel` → accommodation, rooms, hostel facilities, and hostel-related charges
- `timetable` → class schedules and lecture timings
- `examinations` → exam dates, hall tickets, results, registration, and revaluation

---

## 🧠 Deep Learning Model

The chatbot uses a genuine neural-network based intent classifier built with TensorFlow/Keras.

### Architecture

```text
Input Text
    ↓
Tokenization
    ↓
Padding
    ↓
Embedding Layer
    ↓
Bidirectional LSTM
    ↓
Global Max Pooling
    ↓
Dense + ReLU
    ↓
Softmax
    ↓
Predicted Intent
    ↓
Chatbot Response
