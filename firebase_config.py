import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load .env in local dev; in production Render/Railway already injects the ENV vars.
load_dotenv()

# 1) Try to load the full JSON from the FIREBASE_CREDENTIALS env var (production).
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

try:
    cred_dict = json.loads(firebase_credentials_json)
except json.JSONDecodeError as e:
    raise RuntimeError(f"Failed to parse FIREBASE_CREDENTIALS: {e}")
cred = credentials.Certificate(cred_dict)
    
db = firestore.client()