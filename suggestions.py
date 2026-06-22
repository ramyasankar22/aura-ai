from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

def get_suggestion(emotion, user_message, user_name, llm):
    """Generate personalised wellness tips using LLM"""
    
    prompt = f"""You are a wellness expert. Based on this person's message and emotion, give exactly 2 tips.

User name: {user_name}
Emotion detected: {emotion}
What they said: "{user_message}"

Give:
1. ONE mental wellness tip — specific to what they said, not generic
2. ONE physical activity — specific to their energy level and emotion

Rules:
- Each tip max 2 sentences
- Be warm and personal, use their name once
- No bullet points, just plain text
- Separate mental and physical with exactly this marker: [PHYSICAL]

Format:
<mental tip here>
[PHYSICAL]
<physical tip here>"""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content

    # Split into mental and physical
    if "[PHYSICAL]" in content:
        parts = content.split("[PHYSICAL]")
        mental = parts[0].strip()
        physical = parts[1].strip()
    else:
        mental = content.strip()
        physical = "Take a short 10-minute walk outside and breathe deeply."

    return mental, physical