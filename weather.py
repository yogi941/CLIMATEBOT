# weather.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_by_city(city_name):
    """
    Return dict or None. Keys used: weather(desc), main(temp, humidity)
    """
    if not API_KEY or not city_name:
        return None
    # prefer full country name for Bangladesh if missing
    if "," not in city_name:
        city_name = f"{city_name},Bangladesh"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[weather] request failed for {city_name}: {e}")
        return None

def simple_drought_assessment(weather_json):
    """
    Simple heuristic:
      - humidity < 45 and no rain -> dry
      - humidity >=45 -> normal
    Returns {"status": "...", "note": "..."}
    """
    if not weather_json:
        return {"status": "unknown", "note": "Weather data unavailable"}

    desc = weather_json.get("weather", [{}])[0].get("description", "unknown")
    main = weather_json.get("main", {})
    humidity = main.get("humidity")
    temp = main.get("temp")

    has_rain = "rain" in weather_json or ("rain" in desc.lower())

    if humidity is None:
        return {"status": "unknown", "note": f"{desc} (humidity unknown)"}

    note = f"{desc}, Temp: {temp}°C, Humidity: {humidity}%"
    if (not has_rain) and humidity < 45:
        return {"status": "dry", "note": note}
    else:
        return {"status": "normal", "note": note}
