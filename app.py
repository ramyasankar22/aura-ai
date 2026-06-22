import streamlit as st
from database import *
from memory_chain import create_chain, chat
import streamlit.components.v1 as components
from emotion import detect_emotion
from suggestions import get_suggestion
from database import (
    init_db,
    save_message,
    load_messages,
    save_emotion_db,
    get_weekly_insights,
    save_journal,
    load_journals,
)
from graph import build_mood_graph, build_emotion_pie
from auth import show_auth
from speak import speak
from journal_rag import save_journal_with_rag, retrieve_journal_context
import random
from datetime import datetime

st.set_page_config(
    page_title="Aura AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
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

# ──────────────────────────────────────────────
# STYLE
# ──────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        min-width: 360px;
        max-width: 360px;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F5EFE4 !important;
        color: #343148 !important;
    }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none !important; }

    .main .block-container {
        padding: 2rem 2rem 6rem 2rem !important;
        max-width: 100% !important;
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
        font-size: 2.1rem !important;
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
        background-color: #FFFFFF !important;
        border-radius: 4px 18px 18px 18px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        border: 1px solid #E3D5AE !important;
        box-shadow: 0 2px 10px rgba(52, 49, 72, 0.06) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
        color: #2D2A40 !important;
        line-height: 1.6 !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #3D3A58 0%, #2A2840 100%) !important;
        border-radius: 18px 4px 18px 18px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(42, 40, 64, 0.25) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
        color: #F0E4C8 !important;
        line-height: 1.6 !important;
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
    .stButton > button * { color: #D7C49E !important; }

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

    .journal-card {
        background: #4A4560;
        padding: 15px;
        border-radius: 16px;
        border: 1px solid #6B6585;
    }
    textarea {
        background: #4D4868 !important;
        color: #F5EFE4 !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 18px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12), inset 0 1px 1px rgba(255,255,255,0.05);
    }
    textarea::placeholder {
        color: #D7C49E !important;
        opacity: 0.85 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #8B7355 !important;
        opacity: 0.9 !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #343148 !important;
    }

    .rag-pill {
        display: inline-block;
        background: #2a2840;
        color: #D7C49E;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        border: 1px solid #4a4560;
        margin-bottom: 8px;
    }
          .cursor-glow {
        position: fixed;
        width: 220px;
        height: 220px;
        background: radial-gradient(
            circle,
            rgba(235,190,150,0.25),
            rgba(235,190,150,0)
        );
        border-radius: 50%;
        pointer-events: none;
        transform: translate(-50%, -50%);
        z-index: 9999;
    }


    .spark {
        position: fixed;
        width: 6px;
        height: 6px;
        background: #e8c59a;
        border-radius: 50%;
        pointer-events: none;
        animation: fadeSpark 1s ease-out forwards;
    }


    @keyframes fadeSpark {

        0% {
            opacity: 1;
            transform: scale(1);
        }

        100% {
            opacity: 0;
            transform: scale(0) translateY(-40px);
        }

    }

</style>
""", unsafe_allow_html=True)

components.html("""
<script>

const parentDoc = window.parent.document;


let glow = parentDoc.createElement("div");

glow.style.position = "fixed";
glow.style.width = "160px";
glow.style.height = "160px";

glow.style.borderRadius = "50%";

glow.style.pointerEvents = "none";

glow.style.zIndex = "999999";


glow.style.background =
"radial-gradient(circle, rgba(215,196,158,0.35) 0%, rgba(245,239,228,0.05) 45%, transparent 70%)";


glow.style.filter = "blur(8px)";


glow.style.transition =
"left 0.12s ease-out, top 0.12s ease-out";


parentDoc.body.appendChild(glow);



parentDoc.addEventListener("mousemove", function(e){

    glow.style.left = e.clientX - 80 + "px";
    glow.style.top = e.clientY - 80 + "px";

});


</script>
""", height=1)
# ── INIT DB ──
init_db()

# ── AUTH ──
if not show_auth():
    st.stop()

# ── SESSION STATE ──
defaults = {
    "user_name": st.session_state.get("auth_username", "friend"),
    "messages": [],
    "emotion": "neutral",
    "last_response": "",
    "show_graph": False,
    "mental_tip": "Start chatting to get your wellness tip ✨",
    "physical_tip": "Start chatting to get your wellness tip 🌿",
    "daily_quote": random.choice(QUOTES),
    "history_loaded": False,
    "use_journal_context": True,
    "pending_journal_message": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "chain" not in st.session_state:
    st.session_state.chain = create_chain()

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:

    st.markdown("## ✨ Aura")
    st.markdown(f"🌸 Hey, **{st.session_state.user_name.capitalize()}**")
    st.markdown("---")

    # JOURNAL ────────────────────────────────
    with st.expander("📖 Journal", expanded=False):
        st.markdown('<div class="journal-card">', unsafe_allow_html=True)
        journal_text = st.text_area(
            "Write your thoughts...",
            height=250,
            placeholder="Dear Journal... 🌸 What's on your mind today?",
            key="journal_input",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.caption("Saved entries are indexed so Aura can recall them in chat.")

        col_save, col_send = st.columns(2)
        with col_save:
            save_clicked = st.button("💾 Save Journal", key="save_journal_btn")
        with col_send:
            send_clicked = st.button("💬 Send to Aura", key="send_journal_btn")

        if save_clicked:
            if journal_text.strip():
                title = datetime.now().strftime("J-%d-%m-%Y %H:%M")
                # Saves text to DB AND indexes it as a PDF for RAG retrieval
                save_journal_with_rag(
                    username=st.session_state.user_name,
                    title=title,
                    content=journal_text,
                    save_journal_fn=save_journal,
                )
                st.success("Journal saved & indexed 🌸")
            else:
                st.warning("Write something before saving.")

        if send_clicked:
            if journal_text.strip():
                # Also save + index it, same as a normal save, so nothing is lost
                title = datetime.now().strftime("J-%d-%m-%Y %H:%M")
                save_journal_with_rag(
                    username=st.session_state.user_name,
                    title=title,
                    content=journal_text,
                    save_journal_fn=save_journal,
                )
                # Queue it to be sent into the chat on this same rerun
                st.session_state.pending_journal_message = journal_text
                st.rerun()
            else:
                st.warning("Write something before sending.")

        st.markdown("##### Past entries")
        journals = load_journals(st.session_state.user_name)
        for journal in journals[:10]:
            with st.expander(f"📝 {journal['title']}"):
                st.write(journal["content"])

    st.markdown("---")

    # MOOD CHECK ────────────────────────────
    st.markdown("### 😊 Mood Check")
    selected_mood = st.select_slider(
        "",
        options=["😢 Very Sad", "😔 Sad", "😰 Anxious", "😐 Neutral", "🙂 Good", "😊 Happy", "🤩 Amazing"],
        label_visibility="collapsed",
    )

    if st.button("Update Mood"):
        mood_map = {
            "😢 Very Sad": "sad", "😔 Sad": "sad", "😰 Anxious": "anxious",
            "😐 Neutral": "neutral", "🙂 Good": "happy", "😊 Happy": "happy", "🤩 Amazing": "happy",
        }
        emotion = mood_map[selected_mood]
        st.session_state.emotion = emotion
        save_emotion_db(st.session_state.user_name, emotion, "Manual Mood Check")

        mental, physical = get_suggestion(
            emotion, "", st.session_state.user_name, st.session_state.chain
        )
        st.session_state.mental_tip = mental
        st.session_state.physical_tip = physical
        st.success("Mood updated!")
        st.rerun()

    st.markdown("---")

    # TIPS ──────────────────────────────────
    st.markdown("### 💜 Mental Tip")
    st.info(st.session_state.mental_tip)
    st.markdown("### 💪 Physical Tip")
    st.info(st.session_state.physical_tip)
    st.markdown("---")

    # JOURNAL CONTEXT TOGGLE ───────────────
    st.session_state.use_journal_context = st.checkbox(
        "🧠 Let Aura recall journal entries in chat",
        value=st.session_state.use_journal_context,
    )
    st.markdown("---")

    # ANALYTICS ─────────────────────────────
    if st.button("📊 Mood Analytics"):
        st.session_state.show_graph = not st.session_state.show_graph
    st.markdown("---")

    # VOICE ─────────────────────────────────
    if st.session_state.last_response:
        if st.button("🔊 Hear Aura"):
            audio = speak(st.session_state.last_response)
            st.audio(audio, format="audio/mp3", autoplay=True)
    st.markdown("---")

    # RESET / LOGOUT ────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Start Fresh"):
            st.session_state.messages = []
            st.session_state.history_loaded = False
            st.rerun()
    with col_b:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
st.title("✨ Aura AI")
st.markdown(
    '<p class="aura-caption">An intelligent, emotion-aware personal growth companion</p>',
    unsafe_allow_html=True,
)

st.markdown(f"""
<div class="quote-card">
    <p class="quote-text">"{st.session_state.daily_quote}"</p>
    <p class="quote-label">✦ Daily Reflection</p>
</div>
""", unsafe_allow_html=True)

# ── LOAD HISTORY (runs once per session) ──
if not st.session_state.history_loaded:
    past = load_messages(st.session_state.user_name, limit=50)

    if past:
        st.session_state.messages = past
        st.toast(f"🌸 Welcome back, {st.session_state.user_name.capitalize()}!")
    else:
        welcome = (
            f"Hey {st.session_state.user_name.capitalize()}! 🌸 I'm Aura, your personal "
            "growth companion. I'm here to listen, support you, and grow with you every "
            "single day. How are you feeling right now?"
        )
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        save_message(st.session_state.user_name, "assistant", welcome)

    st.session_state.history_loaded = True

# ── CHAT HISTORY ──
AURA_AVATAR = "✨"
USER_AVATAR = "🌸"

for msg in st.session_state.messages:
    avatar = AURA_AVATAR if msg["role"] == "assistant" else USER_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# ── MOOD GRAPH ──
if st.session_state.show_graph:
    with st.expander("📊 Your Mood Journey", expanded=True):
        fig = build_mood_graph(st.session_state.user_name)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        pie = build_emotion_pie(st.session_state.user_name)
        if pie:
            st.plotly_chart(pie, use_container_width=True)
        else:
            st.caption("Chat more to see your mood graph! 🌸")

# ── CHAT INPUT ──
def process_user_message(user_input: str):
    """Runs the full chat turn: emotion detection, RAG lookup, chat() call, save, rerun.
    Used by both the chat input box and the 'Send to Aura' journal button."""
    emotion = detect_emotion(user_input, st.session_state.chain)
    st.session_state.emotion = emotion

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(user_input)

    # RAG: pull relevant journal context for this message
    journal_context = ""
    if st.session_state.use_journal_context:
        journal_context = retrieve_journal_context(
            username=st.session_state.user_name,
            query=user_input,
        )

    with st.chat_message("assistant", avatar=AURA_AVATAR):
        with st.spinner("Aura is thinking..."):
            if journal_context:
                st.markdown('<span class="rag-pill">📖 Recalling your journal</span>', unsafe_allow_html=True)
                augmented_input = (
                    f"{user_input}\n\n"
                    f"[Relevant past journal entries for context — use naturally, "
                    f"don't quote verbatim unless helpful]:\n{journal_context}"
                )
            else:
                augmented_input = user_input

            response = chat(
                st.session_state.chain,
                augmented_input,
                emotion,
                st.session_state.messages[:-1],
                st.session_state.user_name,
            )
            st.write(response)

    st.session_state.last_response = response
    st.session_state.messages.append({"role": "assistant", "content": response})

    save_message(st.session_state.user_name, "user", user_input)
    save_message(st.session_state.user_name, "assistant", response)

    st.rerun()


user_input = st.chat_input(
    f"Share what's on your mind, {st.session_state.user_name.capitalize()}..."
)

if user_input:
    process_user_message(user_input)

# ── Pending journal message (set by the "Send to Aura" button in the sidebar) ──
if st.session_state.get("pending_journal_message"):
    pending = st.session_state.pending_journal_message
    st.session_state.pending_journal_message = None
    process_user_message(pending)