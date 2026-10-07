# 🎙️ Voice-Enabled Chatbot

A web-based **Voice-Enabled University Information Chatbot** built using **Speech Recognition, Deep Learning, and Streamlit**. The system accepts spoken or typed university-related questions, converts speech to text, classifies the user's intent using a **Bi-LSTM neural network**, generates an appropriate response, and provides an automatic browser voice response.

## 🌐 Live Application

**Streamlit App:**  
https://voiceenabledchatbot-m6h2t5dwzipq5abxtxhbx.streamlit.app/

## 📂 Source Code

**GitHub Repository:**  
https://github.com/Sohilshaik07/Voice_Enabled_ChatBot

---

## ✨ Features

- 🎤 Voice-based interaction using browser microphone input
- 📝 Speech-to-text conversion using Google Speech Recognition
- 🧠 Deep-learning based intent classification using Bi-LSTM
- 💬 University-specific chatbot responses
- 🔊 Automatic browser-based text-to-speech response
- ⌨️ Text input fallback when voice input is unavailable
- 🎯 Confidence-based prediction and fallback handling
- 🕘 Conversation history
- 🌐 Deployed online using Streamlit Community Cloud
- 📱 Modern responsive Streamlit interface

---

## 🎯 Supported Intents

The chatbot currently supports **15 university-related intents**:

| Intent | Description |
|---|---|
| Greeting | General greetings |
| Goodbye | Ending a conversation |
| Thanks | Thank-you messages |
| Admission | Admission process and eligibility |
| Courses | Available academic programs |
| Fees | Tuition and fee-related questions |
| Faculty | Faculty-related information |
| Library | Library facilities and services |
| Hostel | Hostel and accommodation information |
| Placements | Placement and career-related information |
| Campus | Campus facilities and information |
| Timetable | Class timetable information |
| Examinations | Examination-related queries |
| Contact | University contact information |
| Scholarships | Scholarship-related information |

---

## 🧠 Deep Learning Model

The chatbot uses a **Bidirectional Long Short-Term Memory (Bi-LSTM)** neural network for intent classification.

### Architecture

```text
Input Text
    ↓
Tokenization
    ↓
Embedding Layer (128 dimensions)
    ↓
Spatial Dropout
    ↓
Bidirectional LSTM (96 units)
    ↓
Global Max Pooling
    ↓
Dropout
    ↓
Dense Layer (96 units, ReLU)
    ↓
Dropout
    ↓
Softmax Output
    ↓
Predicted Intent
```

### Model Training

- Dataset: **450 utterances**
- Number of intents: **15**
- Samples per intent: **30**
- Evaluation split: **80% training / 20% validation**
- Training samples: **360**
- Validation samples: **90**
- Regularization: Dropout + L2 regularization
- Early stopping used to reduce overfitting

### Evaluation Results

| Metric | Score |
|---|---:|
| Training Accuracy | 97.22% |
| Validation Accuracy | 72.22% |
| Weighted Precision | 75.50% |
| Weighted Recall | 72.22% |
| Weighted F1-Score | 72.34% |

The validation results represent performance on held-out data. The difference between training and validation accuracy indicates some generalization gap, which was addressed using dropout, L2 regularization, and early stopping.

> **Note:** The confidence displayed by the application is the model's confidence for an individual prediction. It should not be interpreted as the overall model accuracy.

---

## 🎤 Speech Recognition Pipeline

```text
User Speech
    ↓
Browser Microphone
    ↓
Audio Recording
    ↓
Google Speech Recognition
    ↓
Recognized Text
    ↓
Text Preprocessing
    ↓
Bi-LSTM Intent Classification
    ↓
Response Generation
    ↓
Browser Text-to-Speech
```

The application also supports typed questions as a fallback when voice input is unavailable.

---

## 🔊 Automatic Voice Response

The chatbot automatically reads its response aloud using the browser's native:

```text
SpeechSynthesis API
```

No paid text-to-speech API is required.

The application selects an available natural browser voice when possible and automatically speaks each new chatbot response.

---

## 🛡️ Fallback Handling

The chatbot does not attempt to answer unrelated questions outside its supported university domain.

For example:

```text
User:
What is the weather today?

Chatbot:
I'm sorry, I can currently answer university-related questions
about admissions, courses, fees, faculty, library, hostel,
placements, campus, examinations, scholarships, and related topics.
```

Low-confidence and unsupported queries are handled using the fallback mechanism.

---

## 📁 Project Structure

```text
SLP_MINI_PROJ/
│
├── app.py
├── train.py
├── test_chatbot.py
├── requirements.txt
├── runtime.txt
├── README.md
├── .gitignore
│
├── dataset/
│   └── intents.json
│
├── model/
│   ├── chatbot_model.h5
│   ├── tokenizer.pkl
│   ├── label_encoder.pkl
│   ├── training_metrics.json
│   ├── training_history.json
│   └── confusion_matrix.json
│
├── src/
│   ├── preprocessing.py
│   ├── chatbot.py
│   └── speech_recognition_utils.py
│
└── report/
    └── project_report.md
```

---

## ⚙️ Technologies Used

- **Python 3.11**
- **TensorFlow / Keras**
- **Bi-LSTM**
- **Streamlit**
- **SpeechRecognition**
- **Google Speech Recognition**
- **NumPy**
- **scikit-learn**
- **NLTK / text preprocessing utilities**
- **HTML/CSS**
- **Browser SpeechSynthesis API**
- **Git & GitHub**
- **Streamlit Community Cloud**

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Sohilshaik07/Voice_Enabled_ChatBot.git
cd Voice_Enabled_ChatBot
```

### 2. Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will be available locally through the Streamlit URL shown in the terminal.

---

## 🧪 Testing

The project includes a smoke-test suite covering:

- Intent prediction
- Representative examples for all 15 intents
- Unknown/unsupported query fallback
- Empty text handling
- Empty audio handling
- Model loading
- Prediction pipeline

Run:

```bash
python test_chatbot.py
```

The final local smoke-test run passed all checks.

---

## 📦 Model Artifacts

The trained deployment model and supporting preprocessing artifacts are stored in the `model/` directory:

- `chatbot_model.h5` — trained Bi-LSTM model
- `tokenizer.pkl` — text tokenizer
- `label_encoder.pkl` — intent label encoder
- `training_metrics.json` — evaluation metrics
- `training_history.json` — training history
- `confusion_matrix.json` — confusion matrix data

The Streamlit application loads the existing trained model and does **not** retrain the model during deployment.

---

## ☁️ Deployment

The application is deployed using **Streamlit Community Cloud** directly from the GitHub `main` branch.

Deployment configuration:

```text
Repository: Sohilshaik07/Voice_Enabled_ChatBot
Branch: main
Main file: app.py
Python: 3.11
```

### Live URL

https://voiceenabledchatbot-m6h2t5dwzipq5abxtxhbx.streamlit.app/

---

## ⚠️ Limitations

- The chatbot is limited to the 15 intents represented in the training dataset.
- The dataset is relatively small, so performance on unseen phrasing may vary.
- Google Speech Recognition requires an internet connection.
- Browser microphone and speech-synthesis capabilities depend on browser permissions and support.
- The current chatbot provides predefined intent-based responses rather than open-domain generative answers.

---

## 🔮 Future Improvements

- Expand the dataset with more real-world university queries.
- Add multilingual speech recognition.
- Improve intent classification using transformer-based models.
- Add retrieval-based answers from official university documents.
- Add authentication and personalized student services.
- Integrate university APIs for live timetable, examination, and placement information.
- Improve speech recognition robustness in noisy environments.

---

## 👨‍💻 Project

**Voice-Enabled Chatbot using Speech Recognition and Deep Learning**

Developed as part of the **Speech and Language Processing** mini project.

**GitHub:** https://github.com/Sohilshaik07/Voice_Enabled_ChatBot  
**Live App:** https://voiceenabledchatbot-m6h2t5dwzipq5abxtxhbx.streamlit.app/
