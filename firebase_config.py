import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Always load environment variables (for local dev)
load_dotenv()

# Get FIREBASE_CREDENTIALS from env
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise RuntimeError("FIREBASE_CREDENTIALS environment variable is not set.")

try:
    # Parse JSON string into dict
    firebase_credentials_dict = json.loads(firebase_credentials_json)
except json.JSONDecodeError as e:
    raise RuntimeError(f"Failed to parse FIREBASE_CREDENTIALS JSON: {e}")

# Initialize Firebase
cred = credentials.Certificate(firebase_credentials_dict)
firebase_admin.initialize_app(cred)

# Now Firestore client is safe to create
db = firestore.client()
