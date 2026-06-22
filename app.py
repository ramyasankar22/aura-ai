import streamlit as st
from memory_chain import create_chain, chat
from emotion import detect_emotion
from suggestions import get_suggestion
from database import init_db, save_message, load_messages, save_emotion_db, get_weekly_insights
from graph import build_mood_graph, build_emotion_pie
from auth import show_auth
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

st.markdown("""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
[data-testid="stAppViewContainer"] > div > div {
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
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #D7C49E !important;
    color: #343148 !important;
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
.stChatFloatingInputContainer {
    background-color: #F5EFE4 !important;
    padding: 12px 0 8px 0 !important;
    border-top: 1px solid #E8D9BC !important;
}
.stButton > button {
    background-color: #343148 !important;
    color: #D7C49E !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 24px !important;
}
.stButton > button:hover {
    background-color: #4a4560 !important;
    color: #D7C49E !important;
}
.stButton > button * {
    color: #D7C49E !important;
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

# ── INIT DB ──
init_db()

# ── AUTH ──
if not show_auth():
    st.stop()

# ── SESSION STATE ──
for key, val in {
    "user_name": st.session_state.get("auth_username", "friend"),
    "name_set": True,
    "messages": [],
    "emotion": "neutral",
    "last_response": "",
    "show_graph": False,
    "mental_tip": "Start chatting to get your wellness tip ✨",
    "physical_tip": "Start chatting to get your wellness tip 🌿",
    "daily_quote": random.choice(QUOTES),
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "chain" not in st.session_state:
    st.session_state.chain = create_chain()

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

    # Weekly insights
    insights = get_weekly_insights(st.session_state.user_name)
    if insights:
        st.markdown("---")
        st.markdown("**📈 Weekly insights**")
        emoji_map = {
            "happy": "😊", "sad": "😔",
            "anxious": "😰", "angry": "😤",
            "low energy": "😴", "neutral": "😐"
        }
        mood_lines = "".join([
            f"{emoji_map.get(e,'😐')} {e.title()}: {p}%<br>"
            for e, p in insights['percentages'].items()
        ])
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">Mood Score</div>
            <div class="insight-text" style="font-size:22px;font-weight:500;
                 color:#D7C49E;">{insights['mood_score']}/100</div>
        </div>
        <div class="insight-card">
            <div class="insight-label">This Week</div>
            <div class="insight-text">{mood_lines}</div>
        </div>
        {f'<div class="insight-card"><div class="insight-label">Happiest Day</div><div class="insight-text">{insights["happiest_day"]}</div></div>' if insights["happiest_day"] else ''}
        {f'<div class="insight-card"><div class="insight-label">Stress tends at</div><div class="insight-text">Around {insights["avg_stress_hour"]}:00</div></div>' if insights["avg_stress_hour"] else ''}
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.last_response:
        if st.button("🔊 Hear Aura speak"):
            audio = speak(st.session_state.last_response)
            st.audio(audio, format="audio/mp3", autoplay=True)

    if st.button("🔄 Start Fresh"):
        for key in ["messages", "show_graph", "mental_tip",
                    "physical_tip", "daily_quote", "last_response"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
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

# ── LOAD HISTORY FROM DB ──
if len(st.session_state.messages) == 0:
    past = load_messages(st.session_state.user_name, limit=50)
    if past:
        st.session_state.messages = past
        returning = f"Welcome back, {st.session_state.user_name.capitalize()}! 🌸 I remember you. How have you been since we last talked?"
        st.session_state.messages.append({
            "role": "assistant", "content": returning
        })
    else:
        welcome = f"Hey {st.session_state.user_name.capitalize()}! 🌸 I'm Aura, your personal growth companion. I'm here to listen, support you, and grow with you every single day. How are you feeling right now?"
        st.session_state.messages.append({
            "role": "assistant", "content": welcome
        })
        save_message(st.session_state.user_name, "assistant", welcome)

# ── CHAT HISTORY ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── VOICE BUTTON ──
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
    f"Share what's on your mind, {st.session_state.user_name.capitalize()}..."
)

if user_input:
    emotion = detect_emotion(user_input, st.session_state.chain)
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

    # Save to database
    save_message(st.session_state.user_name, "user", user_input)
    save_message(st.session_state.user_name, "assistant", response)
    save_emotion_db(st.session_state.user_name, emotion, user_input)

    # Get personalised wellness tips
    mental, physical = get_suggestion(
        emotion,
        user_input,
        st.session_state.user_name,
        st.session_state.chain
    )
    st.session_state.mental_tip = mental
    st.session_state.physical_tip = physical
    st.rerun()