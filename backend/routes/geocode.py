from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

# Geocoding API base URL
GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1/search"

@router.get("/geocode")
async def geocode(location: str):
    """Geocode a location name to coordinates"""
    if not location:
        raise HTTPException(status_code=400, detail="Location parameter is missing")
    
    try:
        url = f"{GEOCODING_API_BASE}?name={location}&count=1&format=json"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from geocoding service")
        
        data = response.json()
        if not data.get('results'):
            return {"error": "Location not found"}
        
        result = data['results'][0]
        return {
            "latitude": result.get('latitude'),
            "longitude": result.get('longitude'),
            "city": result.get('name'),
            "country": result.get('country')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")

@router.get("/api/geocode")
async def geocode_api(location: str):
    """Alternative geocode endpoint for frontend compatibility"""
    return await geocode(location)