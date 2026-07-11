import os
import random
import logging
import requests
from typing import Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

class WeatherService:
    @staticmethod
    def get_weather(city: str) -> Dict[str, Any]:
        """
        Fetch weather details for a given city.
        Tries to connect to OpenWeather API if OPENWEATHER_API_KEY is in environment.
        Otherwise, falls back to simulating high-fidelity monsoon weather data.
        """
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            try:
                logger.info(f"Fetching real weather for city: {city} using OpenWeather API.")
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    temp = data["main"]["temp"]
                    humidity = data["main"]["humidity"]
                    wind = data["wind"]["speed"] * 3.6  # convert m/s to km/h
                    # Calculate rain probability descriptor or estimate
                    rain_prob = 0
                    if "rain" in data:
                        rain_prob = 90  # Rain exists in current weather
                    elif "clouds" in data and data["clouds"]["all"] > 50:
                        rain_prob = 60
                    else:
                        rain_prob = random.choice([15, 30, 45])
                    
                    # Estimate Alert level
                    if rain_prob > 80 or wind > 50 or temp > 38:
                        alert_level = "Red Alert"
                    elif rain_prob > 50 or wind > 30:
                        alert_level = "Orange Alert"
                    elif rain_prob > 30:
                        alert_level = "Yellow Alert"
                    else:
                        alert_level = "Normal"
                    
                    return {
                        "temperature": round(temp, 1),
                        "rain_probability": rain_prob,
                        "wind_speed": round(wind, 1),
                        "humidity": humidity,
                        "alert_level": alert_level,
                        "conditions": data["weather"][0]["main"] if data.get("weather") else "Cloudy",
                        "is_mock": False
                    }
                else:
                    logger.warning(f"OpenWeather API returned code {response.status_code}. Using fallback.")
            except Exception as e:
                logger.error(f"Error fetching OpenWeather data: {e}. Using fallback.")
        
        # Fallback simulated data tailored for monsoon demo
        # Seed by city name to keep it consistent per session, but randomized enough to look active
        city_hash = sum(ord(c) for c in city) if city else 100
        random.seed(city_hash)
        
        # Simulate standard monsoon weather for South Asia / tropical regions
        temp = round(random.uniform(24.0, 32.0), 1)
        rain_prob = random.choice([65, 80, 95])  # High rain chance in monsoon
        wind = round(random.uniform(15.0, 48.0), 1)
        humidity = random.randint(75, 98)  # High humidity in monsoon
        
        # Select Alert Level based on rain probability and wind speed
        if rain_prob >= 90 and wind > 35:
            alert_level = "Red Alert (Severe Danger)"
        elif rain_prob >= 80 or wind > 25:
            alert_level = "Orange Alert (Be Prepared)"
        else:
            alert_level = "Yellow Alert (Stay Updated)"
            
        conditions = random.choice(["Heavy Monsoon Rain", "Thunderstorms", "Widespread Showers", "Overcast with Drizzle"])
        
        return {
            "temperature": temp,
            "rain_probability": rain_prob,
            "wind_speed": wind,
            "humidity": humidity,
            "alert_level": alert_level,
            "conditions": conditions,
            "is_mock": True
        }
