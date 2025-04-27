import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise RuntimeError("FIREBASE_CREDENTIALS environment variable is not set.")

# Parse the credentials JSON string
firebase_credentials_dict = json.loads(firebase_credentials_json)

# Create and properly close a temp file
with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
    json.dump(firebase_credentials_dict, temp_file)
    temp_file.flush()
    temp_file_path = temp_file.name  # Save path before closing

# NOW safe to use after file closed
cred = credentials.Certificate(temp_file_path)

firebase_admin.initialize_app(cred)

db = firestore.client()
