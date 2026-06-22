import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from database import load_emotions_db as load_emotions

# Colour mapping for each emotion
EMOTION_COLORS = {
    "happy":      "#FFD700",   # gold
    "sad":        "#4A90D9",   # soft blue
    "anxious":    "#E07B54",   # warm orange
    "angry":      "#E74C3C",   # red
    "low energy": "#A29BFE",   # lavender
    "neutral":    "#95A5A6"    # grey
}

def build_mood_graph():
    """Returns a plotly figure of mood over time"""
    data = load_emotions()
    
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["color"] = df["emotion"].map(EMOTION_COLORS).fillna("#95A5A6")
    
    # Count emotions per day
    daily = df.groupby(["date", "emotion"]).size().reset_index(name="count")
    daily["color"] = daily["emotion"].map(EMOTION_COLORS).fillna("#95A5A6")

    fig = px.scatter(
        daily,
        x="date",
        y="emotion",
        size="count",
        color="emotion",
        color_discrete_map=EMOTION_COLORS,
        title="Your mood journey",
        labels={"date": "Date", "emotion": "Mood", "count": "Times felt"},
        height=350
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        showlegend=True,
        title_font_size=16,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig

def build_emotion_pie(month=None):
    """Pie chart — which emotion dominated this month"""
    data = load_emotions()

    if not data:
        return None

    df = pd.DataFrame(data)

    # Filter by month if given
    if month:
        df = df[df["month"] == month]

    if df.empty:
        return None

    counts = df["emotion"].value_counts().reset_index()
    counts.columns = ["emotion", "count"]
    counts["color"] = counts["emotion"].map(EMOTION_COLORS).fillna("#95A5A6")

    fig = px.pie(
        counts,
        names="emotion",
        values="count",
        color="emotion",
        color_discrete_map=EMOTION_COLORS,
        title="Emotion breakdown",
        height=350,
        width=None
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig