import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_openai_connection():
    try:
        # Test GPT-3.5-turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )
        print("✅ GPT-3.5-turbo working:", response.choices[0].message.content)
        
        # Test TTS
        speech_response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input="Hello World"
        )
        print("✅ TTS working")
        
        return True
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    test_openai_connection() 