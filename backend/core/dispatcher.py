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
    wind_speed = weather_data.get('wind_speed_10m', 0) or weather_data.get('wind_speed_kmh', 0)
    
    print(f"Hero Selection Debug - Backend: time_of_day={time_of_day}, condition={condition_text}, wind_speed={wind_speed}")
    
    # Aquaman for water-related weather (highest priority)
    if any(water_condition in condition_text for water_condition in ['rain', 'drizzle', 'shower', 'storm']):
        print("Selected Hero: Aquaman (water weather)")
        return HERO_PROFILES['aquaman']
    
    # Flash for windy conditions (second priority)
    if 'wind' in condition_text or (wind_speed and wind_speed > 25):
        print("Selected Hero: The Flash (windy conditions)")
        return HERO_PROFILES['the_flash']
    
    # Superman for clear weather during the day
    if time_of_day == 'day' and 'clear' in condition_text:
        print("Selected Hero: Superman (daytime & clear weather)")
        return HERO_PROFILES['superman']
    
    # Wonder Woman for cloudy conditions during the day (no rain)
    if time_of_day == 'day' and any(cloud_condition in condition_text for cloud_condition in ['overcast', 'partly cloud', 'cloud', 'fog']) and not any(rain_condition in condition_text for rain_condition in ['rain', 'drizzle', 'shower', 'storm']):
        print("Selected Hero: Wonder Woman (cloudy day, no rain)")
        return HERO_PROFILES['wonder_woman']
    
    # Batman for night conditions (default for night)
    if time_of_day == 'night':
        print("Selected Hero: Batman (night time)")
        return HERO_PROFILES['batman']
    
    # Default to Batman
    print("Selected Hero: Batman (default)")
    return HERO_PROFILES['batman']