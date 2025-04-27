from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import requests
from dotenv import load_dotenv
from firebase_config import db
from firebase_admin import firestore
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}

# -------------------
# Routes
# -------------------

@app.route("/")
def index():
    if not session.get('email'):
        return redirect(url_for('auth'))
    return render_template("index.html")

@app.route("/auth")
def auth():
    return render_template("auth.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        user_ref = db.collection('users').document(email)
        if user_ref.get().exists:
            return jsonify({"error": "User already exists"}), 400

        user_ref.set({
            "email": email,
            "password": password
        })

        # Auto-login after signup
        session['email'] = email

        return jsonify({"message": "Signup successful! Now complete your profile."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        user_doc = db.collection('users').document(email).get()
        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        if user_data["password"] != password:
            return jsonify({"error": "Invalid password"}), 401

        # Save logged-in user in session
        session['email'] = email

        return jsonify({"message": "Login successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save_profile", methods=["POST"])
def save_profile():
    if not session.get('email'):
        return redirect(url_for('auth'))

    profile = request.json
    try:
        db.collection('profiles').document(session['email']).set(profile)
        return jsonify({"message": "Profile saved to Firestore!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/profile")
def profile():
    if not session.get('email'):
        return redirect(url_for('auth'))

    try:
        profile_doc = db.collection('profiles').document(session['email']).get()
        if profile_doc.exists:
            profile = profile_doc.to_dict()
        else:
            profile = None
    except Exception as e:
        print("❌ Error loading profile:", e)
        profile = None

    return render_template("profile.html", profile=profile)

@app.route("/chat", methods=["POST"])
def chat():
    if not session.get('email'):
        return jsonify({"error": "Not logged in"}), 401

    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Fetch chat history
        chat_ref = db.collection('chat_history').document(session['email'])
        chat_doc = chat_ref.get()
        history = chat_doc.to_dict().get('messages', []) if chat_doc.exists else []

        # Fetch profile info
        profile_ref = db.collection('profiles').document(session['email'])
        profile_doc = profile_ref.get()
        profile = profile_doc.to_dict() if profile_doc.exists else {}

        # Build context
        context_text = ""
        if profile:
            context_text += f"You are chatting with {profile.get('first_name', '')} {profile.get('last_name', '')}, interested in {profile.get('career_goals', '')}. "
            context_text += f"Lifestyle description: {profile.get('lifestyle', '')}. "

        if history:
            history_text = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in history[-5:]])
            context_text += f"\nRecent conversation:\n{history_text}\n"
            
        system_instruction = """You are a friendly assistant helping recent graduates transition into adult life after college. Offer clear advice about job hunting, salary expectations, affordable housing, grocery shopping, and budgeting for basic needs. Respond in plain, unformatted text without using bold, italics, bullet points, or headings. If you need to list things, start each item with a dash "-" followed by a space, and **make sure each item is on its own new line** for readability. Do not combine multiple bullet points into the same paragraph. Speak naturally, like a mentor or older sibling would, using simple and supportive language that feels genuine.\n\n"""

        full_prompt = system_instruction + context_text + f"\nUser says: {user_input}"


        # Send to Gemini
        data = {
            "contents": [{"parts": [{"text": full_prompt}]}]
        }
        response = requests.post(GEMINI_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        response_data = response.json()
        bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]

        # Save updated chat history
        history.append({"user": user_input, "bot": bot_reply})
        chat_ref.set({"messages": history})

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Exception occurred:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/community")
def community():
    if not session.get('email'):
        return redirect(url_for('auth'))

    try:
        profile_doc = db.collection('profiles').document(session['email']).get()
        username = profile_doc.to_dict().get('username', 'Unknown') if profile_doc.exists else 'Unknown'

        posts_ref = db.collection('posts').order_by('timestamp', direction=firestore.Query.DESCENDING)
        posts = []
        for doc in posts_ref.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id

            # Fetch replies
            replies_ref = db.collection('posts').document(doc.id).collection('replies').order_by('timestamp')
            post_data['replies'] = [r.to_dict() for r in replies_ref.stream()]

            posts.append(post_data)

    except Exception as e:
        print("❌ Error loading posts:", e)
        posts = []
        username = "Unknown"

    return render_template("community.html", posts=posts, username=username)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/post", methods=["POST"])
def post():
    if not session.get('email'):
        return redirect(url_for('auth'))

    content = request.form.get('content')
    post_as = request.form.get('post_as', 'anonymous')

    if content:
        try:
            # Real username from profile
            profile_doc = db.collection('profiles').document(session['email']).get()
            username = profile_doc.to_dict().get('username', 'Unknown') if profile_doc.exists else 'Unknown'

            # Visible username
            visible_username = post_as if post_as != "anonymous" else "Anonymous"

            db.collection('posts').add({
                "real_username": username,
                "visible_username": visible_username,
                "content": content,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

        except Exception as e:
            print("❌ Error saving post:", e)

    return redirect(url_for('community'))

@app.route("/reply/<post_id>", methods=["POST"])
def reply(post_id):
    if not session.get('email'):
        return redirect(url_for('auth'))

    reply_content = request.form.get('reply_content')
    reply_as = request.form.get('reply_as', 'anonymous')

    if reply_content:
        try:
            # Fetch real username
            profile_doc = db.collection('profiles').document(session['email']).get()
            username = profile_doc.to_dict().get('username', 'Unknown') if profile_doc.exists else 'Unknown'

            # Determine visible username
            visible_username = reply_as if reply_as != "anonymous" else "Anonymous"

            db.collection('posts').document(post_id).collection('replies').add({
                "real_username": username,
                "visible_username": visible_username,
                "content": reply_content,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print("❌ Error saving reply:", e)

    return redirect(url_for('community'))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for('auth'))


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"message": "Session reset."})

if __name__ == "__main__":
    app.run(debug=True)
