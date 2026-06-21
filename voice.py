import whisper
import speech_recognition as sr
import tempfile
import os

model = whisper.load_model("base")

def transcribe():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        print("Done!")

    # Save to temp wav
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with open(tmp.name, "wb") as f:
        f.write(audio.get_wav_data())

    # Whisper transcribes
    result = model.transcribe(tmp.name)
    os.unlink(tmp.name)
    return result["text"]