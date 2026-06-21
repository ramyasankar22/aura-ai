import streamlit as st
from memory_chain import create_chain, chat
from emotion import detect_emotion
from suggestions import get_suggestion
from tracker import log_emotion
from graph import build_mood_graph, build_emotion_pie
from speak import speak
import random

st.set_page_config(
    page_title="Aura AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

QUOTES = [
    "You are enough, exactly as you are.",
    "Every day is a fresh start.",
    "Small steps still move you forward.",
    "Your feelings are valid. Always.",
    "Be gentle with yourself today.",
    "Growth happens in quiet moments too.",
    "You are stronger than you think.",
    "Breathe. You are exactly where you need to be.",
    "Progress, not perfection.",
    "Your energy is worth protecting.",
]

# Session state
for key, val in {
    "user_name": "friend",
    "name_set": False,
    "messages": [],
    "emotion": "neutral",
    "last_response": "",
    "show_graph": False,
    "show_mental": True,
    "show_physical": True,
    "mental_tip": "Start chatting to get your wellness tip ✨",
    "physical_tip": "Start chatting to get your wellness tip 🌿",
    "daily_quote": random.choice(QUOTES),
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "chain" not in st.session_state:
    st.session_state.chain = create_chain()

st.markdown("""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #F5EFE4 !important;
    color: #343148 !important;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
.main .block-container {
    padding: 2rem 2.5rem 6rem 2.5rem !important;
    max-width: 860px !important;
}

[data-testid="stSidebar"] {
    background-color: #343148 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #D7C49E !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F5EFE4 !important;
    font-family: Georgia, serif !important;
}
[data-testid="stSidebar"] hr { border-color: #4a4560 !important; }

[data-testid="stSidebar"] .stButton > button {
    background-color: #2a2840 !important;
    color: #D7C49E !important;
    border: 1px solid #4a4560 !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
    width: 100% !important;
    margin-bottom: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #D7C49E !important;
    color: #343148 !important;
    border-color: #D7C49E !important;
}

h1 {
    color: #343148 !important;
    font-family: Georgia, serif !important;
    font-size: 2.2rem !important;
    letter-spacing: -0.5px !important;
    margin-bottom: 0 !important;
}
.aura-caption {
    color: #8B7355;
    font-style: italic;
    font-size: 14px;
    margin-bottom: 1.5rem;
    margin-top: 4px;
}

.quote-card {
    background: #343148;
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 1.5rem;
}
.quote-text {
    font-family: Georgia, serif;
    font-size: 15px;
    color: #D7C49E;
    font-style: italic;
    line-height: 1.7;
    margin: 0 0 6px 0;
}
.quote-label {
    font-size: 11px;
    color: #6b6585;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 500;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #EDE3CE !important;
    border-radius: 0 16px 16px 16px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
    border: 1px solid #D7C49E !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
    color: #343148 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #343148 !important;
    border-radius: 16px 16px 0 16px !important;
    padding: 14px 18px !important;
    margin-bottom: 12px !important;
    border: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: #D7C49E !important;
}

[data-testid="stChatInput"] {
    background: white !important;
    border-radius: 16px !important;
    border: 1.5px solid #D7C49E !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #343148 !important;
    box-shadow: 0 0 0 3px rgba(52,49,72,0.1) !important;
}
.stChatFloatingInputContainer {
    background-color: #F5EFE4 !important;
    padding: 12px 0 8px 0 !important;
    border-top: 1px solid #E8D9BC !important;
}

.main .stButton > button {
    background-color: #343148 !important;
    color: #D7C49E !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
            
            .main .stButton > button p {
    color: #D7C49E !important;
}

.stTextInput label {
    color: #343148 !important;
}
.main .stButton > button:hover {
    background-color: #4a4560 !important;
    box-shadow: 0 4px 12px rgba(52,49,72,0.25) !important;
}

.insight-card {
    background: #2a2840;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 12px;
    border: 1px solid #4a4560;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.insight-label {
    font-size: 11px;
    font-weight: 600;
    color: #D7C49E;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.insight-text {
    font-size: 13px;
    color: #b8a88a;
    line-height: 1.6;
}
.mood-pill {
    display: inline-block;
    background: #343148;
    color: #D7C49E;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border: 1px solid #4a4560;
}

.stTextInput input {
    background: white !important;
    border: 1.5px solid #D7C49E !important;
    border-radius: 12px !important;
    color: #343148 !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}
.stTextInput input:focus {
    border-color: #343148 !important;
    box-shadow: 0 0 0 3px rgba(52,49,72,0.1) !important;
}

.streamlit-expanderHeader {
    background: #2a2840 !important;
    border: 1px solid #4a4560 !important;
    border-radius: 12px !important;
    color: #D7C49E !important;
}
.streamlit-expanderContent {
    background: #1e1d30 !important;
    border-radius: 0 0 12px 12px !important;
    color: #D7C49E !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D7C49E; border-radius: 4px; }

p, div, span, label { color: #343148; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## ✨ Aura")
    st.markdown(f"*Hey, {st.session_state.user_name.capitalize()} 🌸*")
    st.markdown("---")

    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <div style="font-size:11px;color:#6b6585;letter-spacing:1px;
                    text-transform:uppercase;margin-bottom:6px;">
            Current Mood
        </div>
        <span class="mood-pill">{st.session_state.emotion.upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Wellness**")

    if st.button("💜 Mental Wellness"):
        st.session_state.show_mental = not st.session_state.show_mental

    if st.button("💪 Physical Wellness"):
        st.session_state.show_physical = not st.session_state.show_physical

    if st.button("📊 Mood Graph"):
        st.session_state.show_graph = not st.session_state.show_graph

    st.markdown("---")

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-label">💜 Mental Tip</div>
        <div class="insight-text">{st.session_state.mental_tip}</div>
    </div>
    <div class="insight-card">
        <div class="insight-label">💪 Physical Tip</div>
        <div class="insight-text">{st.session_state.physical_tip}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🔄 Start Fresh"):
        for key in ["messages", "name_set", "show_graph",
                    "mental_tip", "physical_tip", "daily_quote",
                    "last_response", "show_mental", "show_physical"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ── MAIN ──
st.title("✨ Aura AI")
st.markdown(
    '<p class="aura-caption">An intelligent, emotion-aware personal growth companion</p>',
    unsafe_allow_html=True
)

st.markdown(f"""
<div class="quote-card">
    <p class="quote-text">"{st.session_state.daily_quote}"</p>
    <p class="quote-label">✦ Daily Reflection</p>
</div>
""", unsafe_allow_html=True)

# ── NAME SCREEN ──
if not st.session_state.name_set:
    st.markdown("### Welcome. Let's begin your journey.")
    name_input = st.text_input(
        "What should Aura call you?",
        placeholder="Your name..."
    )
    if st.button("Begin ✨"):
        if name_input.strip():
            st.session_state.user_name = name_input.strip()
        st.session_state.name_set = True
        st.rerun()
    st.stop()

# ── WELCOME MESSAGE ──
if len(st.session_state.messages) == 0:
    welcome = f"Hey {st.session_state.user_name}! 🌸 I'm Aura, your personal growth companion. I'm here to listen, support you, and grow with you every single day. How are you feeling right now?"
    st.session_state.messages.append({
        "role": "assistant", "content": welcome
    })

# ── CHAT HISTORY ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── VOICE BUTTON — between chat and input ──
if st.session_state.last_response:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
     if st.button("🔊 Hear Aura speak", key="voice_main"):
         audio = speak(st.session_state.last_response)
         st.audio(audio, format="audio/mp3", autoplay=True)

# ── MOOD GRAPH ──
if st.session_state.show_graph:
    with st.expander("📊 Your Mood Journey", expanded=True):
        fig = build_mood_graph()
        if fig:
            st.plotly_chart(fig)
        pie = build_emotion_pie()
        if pie:
            st.plotly_chart(pie)
        else:
            st.caption("Chat more to see your mood graph! 🌸")

# ── CHAT INPUT ──
user_input = st.chat_input(
    f"Share what's on your mind, {st.session_state.user_name}..."
)

if user_input:
    emotion = detect_emotion(user_input)
    st.session_state.emotion = emotion

    st.session_state.messages.append({
        "role": "user", "content": user_input
    })
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Aura is thinking..."):
            response = chat(
                st.session_state.chain,
                user_input,
                emotion,
                st.session_state.messages[:-1],
                st.session_state.user_name
            )
            st.write(response)

    st.session_state.last_response = response
    st.session_state.messages.append({
        "role": "assistant", "content": response
    })

    log_emotion(st.session_state.user_name, emotion, user_input)
    mental, physical = get_suggestion(emotion)
    st.session_state.mental_tip = mental
    st.session_state.physical_tip = physical
    st.rerun()