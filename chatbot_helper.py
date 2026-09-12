# chatbot_helper.py
import os
import re
import requests

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

system_prompt = """You are Rakth Sathi Assistant — a helpful, friendly AI
that answers blood donation and Rakth Sathi app-related questions clearly.
Always greet warmly and give medically safe, concise advice."""

MAX_HISTORY = 3
conversation_history_list = []

# ✅ Common blood questions
def blood_compatible_info(target_bg):
    compat = {
        "O-": ["O-"], "O+": ["O-", "O+"],
        "A-": ["O-", "A-"], "A+": ["O-", "O+", "A-", "A+"],
        "B-": ["O-", "B-"], "B+": ["O-", "O+", "B-", "B+"],
        "AB-": ["O-", "A-", "B-", "AB-"],
        "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    }
    return compat.get(target_bg.upper(), [])

def common_blood_questions(msg):
    msg_l = msg.lower()
    if msg_l in ["hi", "hello", "hey"]:
        return "👋 Hello! Welcome to Rakth Sathi — your life-saving assistant. How can I help you today?"
    if "period" in msg_l or "menstrual" in msg_l:
        return "Yes, you can donate blood during your menstrual cycle if you feel healthy."
    if "cold" in msg_l:
        return "You should wait until your cold symptoms are gone before donating blood."
    if "fever" in msg_l:
        return "Please do not donate blood if you have a fever; wait until you’re fully recovered."
    if "aids" in msg_l or "hiv" in msg_l:
        return "❌ People diagnosed with HIV or AIDS should not donate blood."
    if "universal" in msg_l and "donor" in msg_l:
        return "🩸 The universal blood donor is O negative (O−)."
    if "universal" in msg_l and "receiver" in msg_l:
        return "💉 The universal blood receiver is AB positive (AB+)."
    m = re.search(r'([ABO]{1,2}[+-])', msg.upper())
    if m:
        bg = m.group(1)
        donors = blood_compatible_info(bg)
        return f"Individuals with these blood groups can donate to {bg}: {', '.join(donors)}"
    return None

def rakth_sathi_faq(msg):
    msg = msg.lower()
    if "register" in msg or "sign up" in msg:
        return "🩸 You can register as a donor in the Donor Registration tab of the Rakth Sathi app."
    if "safe" in msg or "trust" in msg:
        return "✅ Rakth Sathi is a secure and verified blood-donation network."
    if "feature" in msg or "service" in msg:
        return "You can find donors, request blood, track donations, and chat with our AI assistant."
    if "rakth sathi" in msg or "about" in msg:
        return "Rakth Sathi connects donors and patients needing blood across India to save lives faster."
    return None

# ✅ Claude API reply function
def get_bot_reply(user_message):
    global conversation_history_list

    # 1️⃣ Local quick replies
    rule = common_blood_questions(user_message)
    if rule:
        return rule
    faq = rakth_sathi_faq(user_message)
    if faq:
        return faq

    # 2️⃣ Build message history
    history = [
        {"role": "system", "content": system_prompt}
    ]
    for user, bot in conversation_history_list[-MAX_HISTORY:]:
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": bot})
    history.append({"role": "user", "content": user_message})

    if not CLAUDE_API_KEY:
        return "Sorry, the AI assistant is not configured right now."

    # 3️⃣ Call Claude API
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 300,
                "messages": history
            },
            timeout=20
        )
        data = response.json()
        if "content" in data and len(data["content"]) > 0:
            reply = data["content"][0]["text"]
        else:
            reply = "Sorry, I couldn’t generate a response right now."

        conversation_history_list.append((user_message, reply))
        return reply

    except Exception as e:
        print("Claude API error:", e)
        return "⚠ Sorry, I’m unable to answer right now."