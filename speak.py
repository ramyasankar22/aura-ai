import pyttsx3

def speak(text):
    """Converts Aura's text to speech using pyttsx3 — works offline!"""
    try:
        engine = pyttsx3.init()
        
        # Make voice sound warmer
        engine.setProperty('rate', 150)    # speed — 150 is natural
        engine.setProperty('volume', 0.9)  # volume 0.0 to 1.0
        
        # Try to set female voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        
    except Exception as e:
        print(f"Voice error: {e}")