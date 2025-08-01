from datetime import datetime
from .hero_profiles import HERO_PROFILES

def select_hero(weather_data: dict) -> dict:
    """
    Selects the most appropriate hero based on weather conditions.
    
    Args:
        weather_data (dict): A dictionary containing keys like 'temperature', 
                             'condition_text', 'wind_speed_kmh', 'is_day'.

    Returns:
        dict: The profile of the selected hero.
    """
    time_of_day = 'day' if weather_data.get('is_day', 1) == 1 else 'night'
    condition_text = weather_data.get('condition_text', '').lower()
    
    # First pass: Look for highly specific condition matches
    for hero_id, profile in HERO_PROFILES.items():
        triggers = profile['triggers']
        
        if any(cond_trigger in condition_text for cond_trigger in triggers.get('conditions', [])):
            if hero_id == 'the_flash':
                if weather_data.get('wind_speed_kmh', 0) > triggers.get('wind_speed_kmh_above', 999):
                    return profile
            else:
                 return profile

    # Fallback to default day/night heroes
    if time_of_day == 'night':
        return HERO_PROFILES['batman']
    else:
        return HERO_PROFILES['superman']