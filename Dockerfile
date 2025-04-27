FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GEMINI_API_KEY="AIzaSyC18pXVuglICZx3v_OLxhszx4ItyqCNdOE"

COPY grad2growth-firebase-adminsdk-fbsvc-7911fd6289.json /app/firebase_credentials.json

ENV FIRE-PATH="/app/firebase_credentials.json"

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
