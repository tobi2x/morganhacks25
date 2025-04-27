from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import requests
import hashlib
import bcrypt
from dotenv import load_dotenv
from firebase_config import db
from firebase_admin import firestore
from cryptography.fernet import Fernet
import smtplib
from email.message import EmailMessage
import secrets
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "dev")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}

FERNET_KEY = os.getenv("FERNET_KEY")
cipher = Fernet(FERNET_KEY.encode())

# -------------------
# Helper functions
# -------------------

def hash_sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode('utf-8'))

def send_verification_email(to_email, token):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    verify_link = f"https://www.gradtogrowth.co/verify?token={token}"
    # verify_link = f"http://127.0.0.1:8000/verify?token={token}"


    email = EmailMessage()
    email['Subject'] = 'Verify your email - Grad2Growth'
    email['From'] = smtp_user
    email['To'] = to_email
    email.set_content(f"""
Hi there!

Thanks for signing up for Grad2Growth 🎓✨

Please verify your email by clicking the link below:
{verify_link}

If you didn't sign up, you can ignore this email.

- The Grad2Growth Team
""")

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(email)

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
        hashed_email = hash_sha256(email)
        hashed_password = hash_password(password)
        verification_token = secrets.token_urlsafe(32)

        user_ref = db.collection('users').document(hashed_email)
        if user_ref.get().exists:
            return jsonify({"error": "User already exists"}), 400

        user_ref.set({
            "email": hashed_email,
            "password": hashed_password,
            "verified": False,
            "verification_token": verification_token
        })

        send_verification_email(email, verification_token)

        session['email'] = hashed_email

        return jsonify({"message": "Signup successful! Please check your email to verify."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify")
def verify():
    token = request.args.get('token')
    if not token:
        return render_template('verification_failed.html')

    users_ref = db.collection('users').stream()
    for user in users_ref:
        data = user.to_dict()
        if data.get('verification_token') == token:
            db.collection('users').document(user.id).update({
                "verified": True,
                "verification_token": firestore.DELETE_FIELD
            })
            session['email'] = user.id
            return redirect(url_for('profile'))
    return render_template('verification_failed.html')


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        hashed_email = hash_sha256(email)
        user_doc = db.collection('users').document(hashed_email).get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()

        if not verify_password(password, user_data["password"]):
            return jsonify({"error": "Invalid password"}), 401

        if not user_data.get("verified", False):
            return jsonify({"error": "Email not verified."}), 403

        session['email'] = hashed_email

        return jsonify({"message": "Login successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save_profile", methods=["POST"])
def save_profile():
    if not session.get('email'):
        return redirect(url_for('auth'))

    profile = request.json
    try:
        encrypted_profile = {key: encrypt_data(str(value)) for key, value in profile.items()}
        db.collection('profiles').document(session['email']).set(encrypted_profile)
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
            encrypted_profile = profile_doc.to_dict()
            profile = {key: decrypt_data(value) for key, value in encrypted_profile.items()}
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
        chat_ref = db.collection('chat_history').document(session['email'])
        chat_doc = chat_ref.get()
        history = chat_doc.to_dict().get('messages', []) if chat_doc.exists else []

        profile_ref = db.collection('profiles').document(session['email'])
        profile_doc = profile_ref.get()
        profile = {key: decrypt_data(value) for key, value in profile_doc.to_dict().items()} if profile_doc.exists else {}

        context_text = ""
        if profile:
            context_text += f"You are chatting with {profile.get('first_name', '')} {profile.get('last_name', '')}, interested in {profile.get('career_goals', '')}. "
            context_text += f"Lifestyle description: {profile.get('lifestyle', '')}. "

        if history:
            history_text = "\n".join([f"User: {decrypt_data(msg['user'])}\nBot: {decrypt_data(msg['bot'])}" for msg in history[-5:]])
            context_text += f"\nRecent conversation:\n{history_text}\n"

        system_instruction = """You are a friendly assistant helping recent graduates transition into adult life after college. Offer clear advice about job hunting, salary expectations, affordable housing, grocery shopping, and budgeting for basic needs. Respond in plain, unformatted text without using bold, italics, bullet points, or headings. If you need to list things, start each item with a dash "-" followed by a space, and make sure each item is on its own new line for readability. Speak naturally, like a mentor or older sibling would."""

        full_prompt = system_instruction + context_text + f"\nUser says: {user_input}"

        data = {"contents": [{"parts": [{"text": full_prompt}]}]}
        response = requests.post(GEMINI_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        response_data = response.json()
        bot_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]

        history.append({"user": encrypt_data(user_input), "bot": encrypt_data(bot_reply)})
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
        profile = profile_doc.to_dict()
        username = decrypt_data(profile.get('username')) if profile and 'username' in profile else 'Unknown'

        posts_ref = db.collection('posts').order_by('timestamp', direction=firestore.Query.DESCENDING)
        posts = []
        for doc in posts_ref.stream():
            post_data = doc.to_dict()
            post_data['id'] = doc.id
            post_data['content'] = decrypt_data(post_data['content'])
            post_data['visible_username'] = decrypt_data(post_data['visible_username'])

            replies_ref = db.collection('posts').document(doc.id).collection('replies').order_by('timestamp')
            post_data['replies'] = [{"content": decrypt_data(r.to_dict()['content']), "visible_username": decrypt_data(r.to_dict()['visible_username'])} for r in replies_ref.stream()]

            posts.append(post_data)

    except Exception as e:
        print("❌ Error loading posts:", e)
        posts = []
        username = "Unknown"

    return render_template("community.html", posts=posts, username=username)

@app.route("/post", methods=["POST"])
def post():
    if not session.get('email'):
        return redirect(url_for('auth'))

    content = request.form.get('content')
    post_as = request.form.get('post_as', 'anonymous')

    if content:
        try:
            profile_doc = db.collection('profiles').document(session['email']).get()
            profile = profile_doc.to_dict()
            username = decrypt_data(profile.get('username')) if profile and 'username' in profile else 'Unknown'

            visible_username = username if post_as != "anonymous" else "Anonymous"

            db.collection('posts').add({
                "real_username": encrypt_data(username),
                "visible_username": encrypt_data(visible_username),
                "content": encrypt_data(content),
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
            profile_doc = db.collection('profiles').document(session['email']).get()
            profile = profile_doc.to_dict()
            username = decrypt_data(profile.get('username')) if profile and 'username' in profile else 'Unknown'

            visible_username = username if reply_as != "anonymous" else "Anonymous"

            db.collection('posts').document(post_id).collection('replies').add({
                "real_username": encrypt_data(username),
                "visible_username": encrypt_data(visible_username),
                "content": encrypt_data(reply_content),
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print("❌ Error saving reply:", e)

    return redirect(url_for('community'))

@app.route("/about")
def about():
    return render_template("about.html")

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
