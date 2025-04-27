import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise RuntimeError("FIREBASE_CREDENTIALS environment variable is not set.")

try:
    # Parse the JSON string into a dict
    firebase_credentials_dict = json.loads(firebase_credentials_json)
except json.JSONDecodeError as e:
    raise RuntimeError(f"Failed to parse FIREBASE_CREDENTIALS JSON: {e}")

# Pass the parsed dict (NOT the raw string) to Certificate
cred = credentials.Certificate(firebase_credentials_dict)

firebase_admin.initialize_app(cred)

db = firestore.client()
