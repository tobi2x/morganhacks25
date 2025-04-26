from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev")

GEMINI_API_KEY = os.getenv("GEMINI-API-KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}

# -------------------
# Routes
# -------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/save_profile", methods=["POST"])
def save_profile():
    profile = request.json
    session['profile'] = profile
    session['chat_history'] = []
    session['community_posts'] = []
    return jsonify({"message": "Profile saved!"})

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    profile = session.get("profile", {})
    chat_history = session.get("chat_history", [])

    # Build context for Gemini
    context_text = ""
    if profile:
        context_text += f"You are chatting with {profile.get('first_name', '')} {profile.get('last_name', '')}, interested in {profile.get('career_goals', '')}. "
        context_text += f"Lifestyle description: {profile.get('lifestyle', '')}. "

    if chat_history:
        history_text = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in chat_history[-5:]])
        context_text += f"\nRecent conversation:\n{history_text}\n"

    full_prompt = context_text + f"\nUser says: {user_input}"

    data = {
        "contents": [{"parts": [{"text": full_prompt}]}]
    }

    try:
        response = requests.post(GEMINI_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        response_data = response.json()
        bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]

        chat_history.append({"user": user_input, "bot": bot_reply})
        session['chat_history'] = chat_history

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/profile")
def profile():
    profile = session.get('profile')
    if not profile:
        return redirect(url_for('index'))
    return render_template("profile.html", profile=profile)

@app.route("/community")
def community():
    posts = session.get('community_posts', [])
    return render_template("community.html", posts=posts)

@app.route("/post", methods=["POST"])
def post():
    content = request.form.get("content")
    if content:
        posts = session.get('community_posts', [])
        posts.append(content)
        session['community_posts'] = posts
    return redirect(url_for('community'))

@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"message": "Session reset."})

if __name__ == "__main__":
    app.run(debug=True)