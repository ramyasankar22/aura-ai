# Simple keyword-based emotion detection
# No ML model needed — works perfectly for V1!

def detect_emotion(text):
    text = text.lower()

    sad_words = ["tired", "sad", "cry", "depressed", "lonely",
                 "hopeless", "empty", "hurt", "lost", "fail"]

    anxious_words = ["anxious", "stressed", "worried", "nervous",
                     "scared", "panic", "overwhelmed", "fear", "exam"]

    angry_words = ["angry", "frustrated", "annoyed", "mad",
                   "irritated", "furious", "hate", "upset"]

    happy_words = ["happy", "great", "excited", "good", "amazing",
                   "wonderful", "love", "joy", "fantastic", "proud"]

    low_energy_words = ["lazy", "bored", "dull", "slow",
                        "sluggish", "unmotivated", "drained"]

    # Check which emotion matches most
    if any(word in text for word in sad_words):
        return "sad"
    elif any(word in text for word in anxious_words):
        return "anxious"
    elif any(word in text for word in angry_words):
        return "angry"
    elif any(word in text for word in happy_words):
        return "happy"
    elif any(word in text for word in low_energy_words):
        return "low energy"
    else:
        return "neutral"