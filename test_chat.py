import requests
import json

# ----------------------------
# Configuration
# ----------------------------
# Your Flask backend URL (make sure app.py is running)
API_URL = "http://127.0.0.1:5000/chatbot"

# ----------------------------
# Simple Chat Loop
# ----------------------------
print("🩸 Rakth Sathi Chatbot Test 🩸")
print("Type 'exit' to quit.\n")

while True:
    user_msg = input("You: ").strip()
    if user_msg.lower() in ["exit", "quit", "bye"]:
        print("Assistant: Goodbye! Stay healthy and keep donating blood ❤️")
        break

    try:
        # Send message to Flask API
        payload = {"message": user_msg}
        response = requests.post(API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply") or data.get("error") or "No reply received."
            print("Assistant:", reply)
        else:
            print(f"⚠️ Server error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Flask server not running. Please start 'app.py' first.")
        break
    except requests.exceptions.Timeout:
        print("⏳ The request timed out. Try again.")
    except Exception as e:
        print("❗ Unexpected error:", e)
