import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()
new_line: str = "\n"

api_key: str = os.getenv("GEMINI-API-KEY")

urlx: str = (
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
)

headersx: dict = {
    "Content-Type": "application/json",
}
usr_prompt: str = (
    f"What do you wanna find out from Gemini this lovely saturday? {new_line}"
)
prompt: str = input(usr_prompt)

datax: dict = {"contents": [{"parts": [{"text": prompt}]}]}


def get_reply(url: str, headers: dict, data: dict) -> str:
    try:
        response = requests.post(url, headers=headers, json=data)

        response.raise_for_status()
        response_data: json = response.json()
        # print(json.dumps(response_data, indent=2))
        response_text: str = response_data["candidates"][0]["content"]["parts"][0][
            "text"
        ]
        return f"{new_line}{response_text}"

    except Exception as e:
        print(f"An error occurred: {e}")


x = get_reply(urlx, headersx, datax)

with open("test.md", "w") as file:
    file.write(x)
