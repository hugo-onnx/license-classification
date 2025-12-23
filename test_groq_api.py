import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_connection():
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file.")
        return

    try:
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'API Connection Successful'"
                }
            ],
        )

        print("Success!")
        print(f"Response: {completion.choices[0].message.content}")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_groq_connection()