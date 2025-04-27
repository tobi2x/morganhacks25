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

firebase_credentials_dict = json.loads(firebase_credentials_json)

# Write credentials to a temporary file properly
temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
json.dump(firebase_credentials_dict, temp_file)
temp_file.flush()  # <-- important: write the file to disk
temp_file.seek(0)  # <-- important: move to the start of the file

cred = credentials.Certificate(temp_file.name)

firebase_admin.initialize_app(cred)

db = firestore.client()
