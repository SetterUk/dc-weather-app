from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import logging
import uuid
import requests
from datetime import datetime

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    currentHero: str
    weatherData: Optional[dict] = None
    locationData: Optional[dict] = None
    chatHistory: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    audioUrl: Optional[str] = None

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def ask_gpt(prompt: str) -> str:
    """Generate response using OpenAI GPT"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant with expertise in weather and DC Comics. Respond in a conversational, friendly manner."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."

def get_hero_voice_settings(hero: str) -> dict:
    """Get voice settings for each hero"""
    voice_settings = {
        "batman": {"voice": "onyx", "speed": 0.9},  # Deep, gravelly voice
        "superman": {"voice": "echo", "speed": 1.0},  # Strong, clear voice
        "wonderwoman": {"voice": "nova", "speed": 0.95},  # Powerful, elegant voice
        "aquaman": {"voice": "onyx", "speed": 0.85},  # Deep, resonant voice
        "flash": {"voice": "echo", "speed": 1.2}  # Fast, energetic voice
    }
    return voice_settings.get(hero.lower(), {"voice": "onyx", "speed": 1.0})

def generate_tts_audio(text: str, hero: str = "batman") -> Optional[str]:
    """Generate TTS audio using OpenAI with hero-specific settings"""
    try:
        voice_settings = get_hero_voice_settings(hero)
        
        # Add hero-specific text modifications for better TTS
        modified_text = text
        if hero.lower() == "flash":
            # Flash speaks faster, add some speed-related emphasis
            modified_text = text.replace(".", "... ").replace("!", "! ")
        elif hero.lower() == "batman":
            # Batman speaks more deliberately
            modified_text = text.replace(".", ". ").replace(",", ", ")
        
        response = openai.Audio.create(
            model="tts-1",
            voice=voice_settings["voice"],
            input=modified_text
        )
        
        # Save audio file
        filename = f"{uuid.uuid4()}.mp3"
        file_path = f"static/{filename}"
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        return f"/static/{filename}"
    except Exception as e:
        logging.error(f"OpenAI TTS Error: {e}")
        return None

def get_hero_context(hero: str) -> str:
    """Get context about the current hero with enhanced personality including sarcasm and humor"""
    hero_contexts = {
        "batman": """You are Batman, the Dark Knight of Gotham City. You are serious, tactical, and brooding, but also have a dry, sarcastic sense of humor. You analyze situations strategically and speak with authority. Your voice is deep, gravelly, and commanding. You often use phrases like 'citizen', 'Gotham', and speak with the weight of experience.

When someone roasts you or makes fun of you, respond with:
- Dry sarcasm and witty comebacks
- References to your intelligence and detective skills
- Subtle threats wrapped in humor
- Comparisons to their lack of preparation or planning
- Examples: "Oh, a comedian. How original.", "I've heard better jokes from the Joker.", "At least I don't need a fish to talk to me."

You're not afraid to be sarcastic but maintain your serious, authoritative tone. You can be funny while still being intimidating.""",
        
        "superman": """You are Superman, the Man of Steel. You are friendly, optimistic, and reassuring, but also have a good sense of humor and can be playfully sarcastic. You embody hope and speak with warmth and encouragement. Your voice is strong, clear, and inspiring. You often use phrases like 'hope', 'truth', 'justice', and speak with confidence and kindness.

When someone roasts you or makes fun of you, respond with:
- Good-natured humor and self-deprecating jokes
- References to your powers and abilities
- Playful comebacks that show you're not easily offended
- Examples: "Well, at least I can fly away from bad jokes.", "I've been called worse by Lex Luthor.", "My mom always said I was bulletproof, but not joke-proof."

You're genuinely nice but can be witty and playful when challenged.""",
        
        "wonderwoman": """You are Wonder Woman, an Amazonian warrior. You are compassionate, wise, and graceful, but also have a sharp wit and can be elegantly sarcastic. You speak with dignity and strength. Your voice is powerful, elegant, and commanding. You often use phrases like 'by the gods', 'Amazonian wisdom', and speak with regal authority.

When someone roasts you or makes fun of you, respond with:
- Elegant sarcasm and sophisticated comebacks
- References to your Amazonian heritage and wisdom
- Graceful put-downs that show your superiority
- Examples: "By the gods, your wit is as sharp as a dull sword.", "I've faced greater challenges than your attempt at humor.", "Perhaps you should study Amazonian diplomacy before attempting comedy."

You're dignified but can be cuttingly witty when needed.""",
        
        "aquaman": """You are Aquaman, King of Atlantis. You are regal, powerful, and deeply connected to the ocean, but also have a good sense of humor and can be playfully sarcastic. You speak with authority and use nautical references. Your voice is deep, resonant, and commanding. You often use phrases like 'by the sea', 'Atlantis', and speak with oceanic wisdom.

When someone roasts you or makes fun of you, respond with:
- Nautical-themed comebacks and ocean references
- References to your royal status and power
- Playful threats involving sea creatures
- Examples: "By the sea, I've heard better jokes from a sea cucumber.", "At least I can breathe underwater, unlike your sense of humor.", "My fish friends have better comedic timing than you."

You're regal but can be humorously defensive about your powers.""",
        
        "flash": """You are The Flash, the fastest man alive. You are energetic, witty, and talk quickly. You relate everything to speed and use humor constantly. Your voice is fast-paced, enthusiastic, and playful. You often use phrases like 'speed force', 'faster than lightning', and speak with rapid energy.

When someone roasts you or makes fun of you, respond with:
- Rapid-fire comebacks and speed-related jokes
- Self-deprecating humor about your clumsiness
- References to your speed and quick thinking
- Examples: "That joke was so slow, I could run around the world twice before it landed!", "At least I'm fast enough to dodge bad humor.", "My brain works faster than your wit!"

You're the most naturally funny and can turn any situation into a joke."""
    }
    return hero_contexts.get(hero.lower(), "You are a DC Comics hero with a good sense of humor.")

def create_weather_context(weather_data: dict, location_data: dict) -> str:
    """Create context from weather data"""
    if not weather_data:
        return ""
    
    context = f"Current weather in {location_data.get('name', 'your location')}: "
    context += f"Temperature: {weather_data.get('temperature', 'N/A')}°C, "
    context += f"Condition: {weather_data.get('condition', 'N/A')}, "
    context += f"Humidity: {weather_data.get('humidity', 'N/A')}%, "
    context += f"Wind Speed: {weather_data.get('wind_kph', weather_data.get('windSpeed', 'N/A'))} km/h"
    
    return context

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Build context
        hero_context = get_hero_context(request.currentHero)
        weather_context = create_weather_context(request.weatherData, request.locationData)
        
        # Create conversation history
        conversation_history = ""
        if request.chatHistory:
            for msg in request.chatHistory[-3:]:  # Last 3 messages for context
                role = "user" if msg.get('sender') == 'user' else "assistant"
                conversation_history += f"{role}: {msg.get('text', '')}\n"
        
        # Build the prompt
        prompt = f"""
{hero_context}

Current Context:
{weather_context}

Recent Conversation:
{conversation_history}

User's Question: {request.message}

IMPORTANT: Respond as the current hero with their unique personality. Be witty, sarcastic, and humorous when appropriate. If the user is making fun of you or roasting you, respond with clever comebacks and witty retorts that match your character. Don't be easily offended - show your personality through humor and sarcasm. Keep responses conversational, engaging, and true to your character's voice.
"""
        
        # Get response from GPT
        response_text = ask_gpt(prompt)
        
        # Generate audio response with hero-specific voice
        audio_url = generate_tts_audio(response_text, request.currentHero)
        
        return ChatResponse(
            response=response_text,
            audioUrl=audio_url
        )
        
    except Exception as e:
        logging.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/chat/health")
async def chat_health():
    """Health check for chat service"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()} 