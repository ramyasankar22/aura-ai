import csv
import os
from datetime import datetime

TRACKER_FILE = "emotion_log.csv"

def log_emotion(user_name, emotion, message):
    """Save every detected emotion with timestamp"""
    
    # Create file with headers if it doesn't exist
    file_exists = os.path.exists(TRACKER_FILE)
    
    with open(TRACKER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date", "time", "month", "user", "emotion", "message"
        ])
        
        if not file_exists:
            writer.writeheader()  # write headers only once
        
        now = datetime.now()
        writer.writerow({
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "month": now.strftime("%B %Y"),
            "user": user_name,
            "emotion": emotion,
            "message": message[:100]  # save first 100 chars only
        })

def load_emotions():
    """Load all saved emotions as a list of dicts"""
    if not os.path.exists(TRACKER_FILE):
        return []
    
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)