import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise Exception("FIREBASE_CREDENTIALS is not set.")

try:
    firebase_credentials_dict = json.loads(firebase_credentials_json)
except Exception as e:
    raise Exception(f"Failed to parse FIREBASE_CREDENTIALS env var: {e}")

with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp:
    json.dump(firebase_credentials_dict, temp)
    temp.flush()
    temp_name = temp.name  
    
cred = credentials.Certificate(temp_name)

firebase_admin.initialize_app(cred)

db = firestore.client()