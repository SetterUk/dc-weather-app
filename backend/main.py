import os
import re
import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import logging

# Import our custom modules
from core.hero_profiles import HERO_PROFILES
from core.dispatcher import select_hero

# Import routes
from routes.geocode import router as geocode_router

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Include routers
app.include_router(geocode_router)

# --- Create a directory for static files (audio) and mount it ---
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Clients and Constants ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1/search"
REVERSE_GEOCODING_API_BASE = "https://api.bigdatacloud.net/data/reverse-geocode-client"
WEATHER_API_BASE = "https://api.open-meteo.com/v1/forecast"
WMO_WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

# --- Pydantic Models ---
class WeatherRequest(BaseModel):
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    chat_history: Optional[list] = []


# --- Helper Functions ---
def get_location_coords(location_name: str):
    url = f"{GEOCODING_API_BASE}?name={location_name}&count=1&format=json"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('results'):
        return response.json()['results'][0]
    return None

def get_location_name_from_coords(lat: float, lon: float):
    url = f"{REVERSE_GEOCODING_API_BASE}?latitude={lat}&longitude={lon}&localityLanguage=en"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"{data.get('city', '')}, {data.get('countryName', '')}"
    return "Current Location"


def get_full_weather_forecast(lat: float, lon: float):
    # Enhanced parameters to get more comprehensive weather data
    params = {
        "latitude": lat, 
        "longitude": lon, 
        "current": "temperature_2m,is_day,weather_code,wind_speed_10m,relative_humidity_2m,apparent_temperature,pressure_msl,precipitation,cloud_cover",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,winddirection_10m_dominant",
        "hourly": "temperature_2m,weather_code,relative_humidity_2m,apparent_temperature,precipitation_probability,windspeed_10m",
        "timezone": "auto", 
        "forecast_days": 7
    }
    response = requests.get(WEATHER_API_BASE, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Set up logging to file
logging.basicConfig(filename='backend_error.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(message)s')

def ask_gpt(prompt: str):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You are a helpful assistant embodying a DC Comics character."}, {"role": "user", "content": prompt}], temperature=0.7, max_tokens=250)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error (GPT): {e}")
        logging.error(f"OpenAI API Error (GPT): {e}")
        # Generate fallback dialogue based on hero and weather
        return generate_fallback_dialogue(prompt)

def generate_fallback_dialogue(prompt: str):
    """Generate basic hero dialogue when OpenAI API is unavailable"""
    if "Batman" in prompt:
        return "Citizen, the weather conditions are clear for tonight's patrol. Stay vigilant."
    elif "Superman" in prompt:
        return "The sun's energy is strong today, perfect for keeping Metropolis safe."
    elif "Wonder Woman" in prompt:
        return "The gods have blessed us with fair weather today."
    elif "Aquaman" in prompt:
        return "The ocean's power flows through the rain. Atlantis stands strong."
    elif "Flash" in prompt:
        return "Speed force is optimal today! Perfect conditions for a quick run."
    else:
        return "The Watchtower systems are experiencing temporary issues. Weather data is still available, but AI responses are limited."

# DALL-E image generation removed since 3D models are used instead

def generate_tts_audio(text: str, voice: str = "onyx"):
    """Generates speech from text and saves it as a static file."""
    try:
        filename = f"{uuid.uuid4()}.mp3"
        speech_file_path = os.path.join("static", filename)
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(speech_file_path)
        return f"/static/{filename}"
    except Exception as e:
        print(f"OpenAI API Error (TTS): {e}")
        logging.error(f"OpenAI API Error (TTS): {e}")
        return None

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"Status": "Watchtower API is online"}

@app.post("/api/get-weather-dashboard")
def get_weather_dashboard_endpoint(request: WeatherRequest):
    coords = None
    location_display_name = "an unknown location"

    if request.latitude is not None and request.longitude is not None:
        coords = {"latitude": request.latitude, "longitude": request.longitude}
        location_display_name = get_location_name_from_coords(request.latitude, request.longitude)
    elif request.location:
        location_data = get_location_coords(request.location)
        if not location_data:
            raise HTTPException(status_code=404, detail=f"Location '{request.location}' not found.")
        coords = location_data
        location_display_name = coords.get('name', request.location)
    else:
        raise HTTPException(status_code=400, detail="Either location name or coordinates must be provided.")

    full_weather_data = get_full_weather_forecast(coords['latitude'], coords['longitude'])
    if not full_weather_data:
        raise HTTPException(status_code=500, detail="Could not retrieve weather data.")

    current_weather = full_weather_data.get('current', {})
    current_weather['condition_text'] = WMO_WEATHER_CODES.get(current_weather.get('weather_code', 0), 'Unknown')
    # Map to frontend expected keys with enhanced Open-Meteo data
    mapped_current_weather = {
        'temperature': current_weather.get('temperature_2m'),
        'condition': current_weather.get('condition_text'),
        'humidity': current_weather.get('relative_humidity_2m'),
        'windSpeed': current_weather.get('wind_speed_10m'),
        'feelsLike': current_weather.get('apparent_temperature'),
        'aqi': None,  # Open-Meteo does not provide AQI
        'wind_kph': current_weather.get('wind_speed_10m'),
        'humidity': current_weather.get('relative_humidity_2m'),
        'time': current_weather.get('time'),
        'pressure': current_weather.get('pressure_msl'),
        'precipitation': current_weather.get('precipitation'),
        'cloudCover': current_weather.get('cloud_cover'),
        'isDay': current_weather.get('is_day'),
    }
    
    hero_profile = select_hero(current_weather)

    user_query = request.chat_history[-1]['content'] if request.chat_history and len(request.chat_history) > 0 else "Give me a weather report."
    
    master_prompt = f"""
    You are {hero_profile['name']}. Your mission is to act as a weather commentator.
    **Your Persona:** {hero_profile['persona']}
    **Location:** {location_display_name}
    **Current Weather:** {current_weather.get('temperature_2m')}°C, {current_weather['condition_text']}
    **User's Latest Message:** "{user_query}"
    Based on the user's message and the weather, provide a brief, in-character response.
    """
    dialogue = ask_gpt(master_prompt)

    # Skip DALL-E image generation since we have 3D models
    image_url = None

    # Generate the audio for the dialogue
    audio_url = generate_tts_audio(dialogue, hero_profile.get("voice", "onyx"))


    daily_forecast = full_weather_data.get('daily', {})
    formatted_daily = []
    if daily_forecast.get('time'):
        for i, date in enumerate(daily_forecast['time']):
            formatted_daily.append({
                'date': date,
                'day': datetime.strptime(date, "%Y-%m-%d").strftime("%A"),
                'weather_code': daily_forecast['weather_code'][i],
                'condition': WMO_WEATHER_CODES.get(daily_forecast['weather_code'][i], "Unknown"),
                'minTemp': daily_forecast['temperature_2m_min'][i],
                'maxTemp': daily_forecast['temperature_2m_max'][i],
                'precipitation': daily_forecast.get('precipitation_sum', [None] * len(daily_forecast['time']))[i],
                'precipitationProbability': daily_forecast.get('precipitation_probability_max', [None] * len(daily_forecast['time']))[i],
                'windSpeed': daily_forecast.get('windspeed_10m_max', [None] * len(daily_forecast['time']))[i],
                'windDirection': daily_forecast.get('winddirection_10m_dominant', [None] * len(daily_forecast['time']))[i],
            })

    return {
        'location': {"name": location_display_name, "latitude": coords['latitude'], "longitude": coords['longitude']},
        'currentWeather': mapped_current_weather,
        'dailyForecast': formatted_daily,
        'hero': {"name": hero_profile['name'], "dialogue": dialogue, "imageUrl": image_url, "audioUrl": audio_url}
    }

@app.get("/api/weather")
async def get_weather(latitude: float, longitude: float, city: Optional[str] = None):
    return await get_weather_dashboard_endpoint(WeatherRequest(latitude=latitude, longitude=longitude, city=city))