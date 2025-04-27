import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# firebase_path = os.getenv("FIRE-PATH")
# if not firebase_path:
#     raise Exception("FIRE-PATH not set in .env file")

# cred = credentials.Certificate(firebase_path)
# firebase_admin.initialize_app(cred)

# db = firestore.client()

# firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

# if firebase_credentials_json:
#     cred_dict = json.loads(firebase_credentials_json)
#     cred = credentials.Certificate(cred_dict)
# else:
#     firebase_path = os.getenv("FIRE_PATH")
#     if not firebase_path:
#         raise Exception("Neither FIREBASE_CREDENTIALS nor FIRE_PATH is set.")
#     cred = credentials.Certificate(firebase_path)

# firebase_admin.initialize_app(cred)
# db = firestore.client()

# firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")
# cred_dict = json.loads(firebase_credentials_json)
# cred = credentials.Certificate(cred_dict)
# firebase_admin.initialize_app(cred)
# db = firestore.client()

load_dotenv()

firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise Exception("FIREBASE_CREDENTIALS is not set.")

try:
    # Make sure it's loaded as a dict
    firebase_credentials_dict = json.loads(firebase_credentials_json)
except Exception as e:
    raise Exception(f"Failed to parse FIREBASE_CREDENTIALS: {e}")

# ✅ Pass the dictionary directly!
cred = credentials.Certificate(firebase_credentials_dict)

firebase_admin.initialize_app(cred)

db = firestore.client()