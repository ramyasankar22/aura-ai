# Maps emotion → mental + physical suggestions

suggestions = {
    "sad": {
        "mental": [
            "Write 3 things you are grateful for today",
            "Give yourself a hug — you are doing your best",
            "Listen to your favourite song for 5 minutes",
            "Talk to someone you trust today"
        ],
        "physical": [
            "Try Child's Pose yoga for 5 minutes",
            "Go for a slow 10-minute walk outside",
            "Do 5 deep belly breaths right now",
            "Gentle full-body stretch — 10 minutes"
        ]
    },
    "anxious": {
        "mental": [
            "Try box breathing: inhale 4s, hold 4s, exhale 4s",
            "Write down your worries — then close the notebook",
            "Remind yourself: this feeling will pass",
            "5-4-3-2-1 grounding: name 5 things you can see"
        ],
        "physical": [
            "10 minutes of yoga Nidra (body scan)",
            "Shake your hands and arms out for 1 minute",
            "Cold water on your face — activates calm reflex",
            "Slow neck rolls left and right — release tension"
        ]
    },
    "angry": {
        "mental": [
            "Write a letter you will never send — let it out",
            "Count backwards from 10 slowly",
            "Ask yourself: will this matter in 1 year?",
            "Take a 5-minute break before responding to anyone"
        ],
        "physical": [
            "Do 20 jumping jacks — burn the energy",
            "Punch a pillow or do shadow boxing for 2 minutes",
            "Run in place for 60 seconds",
            "Power yoga sun salutation — 5 rounds"
        ]
    },
    "happy": {
        "mental": [
            "Write down what made you feel this good today",
            "Share your happiness with someone you love",
            "Set one new goal while your energy is high",
            "Celebrate yourself — you deserve it!"
        ],
        "physical": [
            "Dance to your favourite song right now!",
            "Try a new workout you have been curious about",
            "Morning run — channel this energy!",
            "Power pose for 2 minutes — own this feeling"
        ]
    },
    "low energy": {
        "mental": [
            "It is okay to rest — rest is productive",
            "Do one tiny task to feel momentum",
            "Watch something that inspires you for 10 minutes",
            "Make a simple to-do list for just today"
        ],
        "physical": [
            "5-minute morning stretch in bed",
            "Drink a full glass of water right now",
            "10-minute Yoga with Adriene energising flow",
            "Step outside for 5 minutes of sunlight"
        ]
    },
    "neutral": {
        "mental": [
            "Reflect: what is one thing you want to improve?",
            "Read something inspiring for 10 minutes",
            "Meditate for 5 minutes — just observe your breath",
            "Journal: how do you want to feel by tonight?"
        ],
        "physical": [
            "30-minute moderate workout of your choice",
            "Try a new yoga pose today",
            "Evening walk while listening to a podcast",
            "Stretch your back and shoulders — desk posture check"
        ]
    }
}

import random

def get_suggestion(emotion):
    data = suggestions.get(emotion, suggestions["neutral"])
    mental = random.choice(data["mental"])
    physical = random.choice(data["physical"])
    return mental, physical