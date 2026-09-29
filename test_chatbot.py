"""Smoke tests for trained chatbot artifacts. Run after `python train.py`."""
from src.chatbot import load_artifacts, load_responses, reply_for
from src.speech_recognition_utils import transcribe_wav

CASES = {
    "Hello": "greeting", "Goodbye": "goodbye", "Thank you": "thanks",
    "How do I apply?": "admission", "What courses are available?": "courses",
    "How much are the fees?": "fees", "Who are the professors?": "faculty",
    "Can I borrow books?": "library", "Does the college have hostels?": "hostel",
    "Tell me about placements": "placements", "Tell me about campus": "campus",
    "Where is my timetable?": "timetable", "When are exams?": "examinations",
    "What is the college phone number?": "contact", "Are scholarships available?": "scholarships",
    "Good morning, can you help me?": "greeting", "I am done with my questions": "goodbye",
    "I appreciate your support": "thanks", "What documents are needed for admission?": "admission",
    "Which degrees can I choose?": "courses", "Can I pay tuition online?": "fees",
    "How can I contact a professor?": "faculty", "Can I renew a borrowed book?": "library",
    "Is WiFi available in the hostel?": "hostel", "Do you provide interview preparation?": "placements",
    "Is there a campus bus service?": "campus", "What time is my next lecture?": "timetable",
    "How do I download my hall ticket?": "examinations", "What is the official university email?": "contact",
    "How do I renew my scholarship?": "scholarships",
}

def main():
    model, tokenizer, encoder = load_artifacts(); responses = load_responses()
    failures = []
    for text, expected in CASES.items():
        actual, confidence, response = reply_for(text, model, tokenizer, encoder, responses)
        print(f"{text!r} -> {actual} ({confidence:.1%}): {response}")
        if actual != expected: failures.append(f"{text}: expected {expected}, got {actual}")
    for question in ["What is the weather forecast on Mars?", "What is the weather today?", "How do I cook pasta?"]:
        unknown_intent, _, _ = reply_for(question, model, tokenizer, encoder, responses)
        assert unknown_intent is None, f"Unrelated question should use the fallback response: {question}"
    empty_intent, _, _ = reply_for("   ", model, tokenizer, encoder, responses)
    assert empty_intent is None, "Empty text should not be classified"
    speech, error = transcribe_wav(b"")
    assert speech is None and error, "Empty audio should produce a graceful speech-recognition error"
    assert not failures, "\n".join(failures)
    print("All smoke tests passed.")

if __name__ == "__main__": main()
