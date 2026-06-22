from langchain_core.messages import HumanMessage

def detect_emotion(text, llm):
    """Use Groq LLM to detect emotion — understands context deeply!"""
    
    prompt = f"""Classify the emotion in this message into exactly ONE word.
Choose from: happy, sad, anxious, angry, low energy, neutral

Examples:
"I failed my exam" → sad
"I have so much to do and no time" → anxious  
"I feel like doing nothing today" → low energy
"I just got placed!" → happy
"Everyone is annoying me" → angry
"Just another day" → neutral

Message: "{text}"

Reply with ONLY the emotion word, nothing else. No punctuation, no explanation."""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        emotion = response.content.strip().lower()
        
        # Remove any punctuation just in case
        emotion = emotion.replace(".", "").replace(",", "").strip()
        
        valid = ["happy", "sad", "anxious", "angry", "low energy", "neutral"]
        
        if emotion in valid:
            return emotion
        else:
            return "neutral"
            
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return fallback_detect(text)

def fallback_detect(text):
    """Backup if LLM call fails"""
    text = text.lower()
    if any(w in text for w in ["tired","sad","cry","depressed","lonely","hurt","failed"]):
        return "sad"
    elif any(w in text for w in ["anxious","stressed","worried","scared","exam","panic","overwhelmed"]):
        return "anxious"
    elif any(w in text for w in ["angry","frustrated","annoyed","mad","hate","irritated"]):
        return "angry"
    elif any(w in text for w in ["happy","great","excited","good","amazing","proud","love"]):
        return "happy"
    elif any(w in text for w in ["lazy","bored","dull","unmotivated","drained","nothing"]):
        return "low energy"
    else:
        return "neutral"