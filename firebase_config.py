import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

firebase_path = os.getenv("FIRE-PATH")
if not firebase_path:
    raise Exception("FIRE-PATH not set in .env file")

cred = credentials.Certificate(firebase_path)
firebase_admin.initialize_app(cred)

db = firestore.client()
