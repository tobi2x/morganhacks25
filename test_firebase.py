# test_firebase.py
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

firebase_path = os.getenv("FIRE-PATH")


def main():
    try:
        # Load credentials
        cred = credentials.Certificate(firebase_path)  # Path to your downloaded key
        firebase_admin.initialize_app(cred)

        # Get Firestore client
        db = firestore.client()

        print("✅ Connected to Firestore!")

        # Test: Insert a dummy document into "profiles" collection
        profile_data = {
            "first_name": "Testy",
            "last_name": "McTestface",
            "email": "test@example.com",
            "career_goals": "Testing Engineer",
            "lifestyle": "Sleepy",
        }
        result = db.collection("profiles").add(profile_data)
        print(f"✅ Inserted document with ID: {result[1].id}")

        # Test: Fetch documents
        profiles_ref = db.collection("profiles")
        docs = profiles_ref.stream()
        print("✅ Retrieved profiles:")
        for doc in docs:
            print(f"{doc.id} => {doc.to_dict()}")

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()
