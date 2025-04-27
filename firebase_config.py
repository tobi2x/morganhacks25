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

try:
    firebase_credentials_dict = json.loads(firebase_credentials_json)
except json.JSONDecodeError as e:
    raise RuntimeError(f"Invalid FIREBASE_CREDENTIALS JSON: {e}")

# Write credentials to a temporary file
temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
json.dump(firebase_credentials_dict, temp_file)
temp_file.close()

# Pass the path of the temporary file to Certificate
cred = credentials.Certificate(temp_file.name)

firebase_admin.initialize_app(cred)

db = firestore.client()
