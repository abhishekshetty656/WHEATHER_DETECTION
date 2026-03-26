import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

REQUEST_TIMEOUT = 10
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
REVERSE_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/reverse"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_MAP = {
    0: {"condition": "Clear", "description": "Clear sky", "day_icon": "clear-day-fill", "night_icon": "clear-night-fill", "day_theme": "clear", "night_theme": "night-clear"},
    1: {"condition": "Mostly Clear", "description": "Mostly clear", "day_icon": "clear-day-fill", "night_icon": "clear-night-fill", "day_theme": "clear", "night_theme": "night-clear"},
    2: {"condition": "Partly Cloudy", "description": "Partly cloudy", "day_icon": "partly-cloudy-day-fill", "night_icon": "partly-cloudy-night-fill", "day_theme": "clouds", "night_theme": "night-clouds"},
    3: {"condition": "Cloudy", "description": "Overcast skies", "day_icon": "cloudy-fill", "night_icon": "cloudy-fill", "day_theme": "clouds", "night_theme": "night-clouds"},
    45: {"condition": "Mist", "description": "Foggy conditions", "day_icon": "fog-fill", "night_icon": "fog-fill", "day_theme": "mist", "night_theme": "mist"},
    48: {"condition": "Mist", "description": "Depositing rime fog", "day_icon": "fog-fill", "night_icon": "fog-fill", "day_theme": "mist", "night_theme": "mist"},
    51: {"condition": "Drizzle", "description": "Light drizzle", "day_icon": "drizzle-fill", "night_icon": "drizzle-fill", "day_theme": "rain", "night_theme": "rain"},
    53: {"condition": "Drizzle", "description": "Moderate drizzle", "day_icon": "drizzle-fill", "night_icon": "drizzle-fill", "day_theme": "rain", "night_theme": "rain"},
    55: {"condition": "Drizzle", "description": "Heavy drizzle", "day_icon": "extreme-drizzle-fill", "night_icon": "extreme-drizzle-fill", "day_theme": "rain", "night_theme": "rain"},
    61: {"condition": "Rain", "description": "Light rain", "day_icon": "rain-fill", "night_icon": "rain-fill", "day_theme": "rain", "night_theme": "rain"},
    63: {"condition": "Rain", "description": "Moderate rain", "day_icon": "rain-fill", "night_icon": "rain-fill", "day_theme": "rain", "night_theme": "rain"},
    65: {"condition": "Rain", "description": "Heavy rain", "day_icon": "extreme-rain-fill", "night_icon": "extreme-rain-fill", "day_theme": "rain", "night_theme": "rain"},
    71: {"condition": "Snow", "description": "Light snow", "day_icon": "snow-fill", "night_icon": "snow-fill", "day_theme": "snow", "night_theme": "snow"},
    73: {"condition": "Snow", "description": "Moderate snow", "day_icon": "snow-fill", "night_icon": "snow-fill", "day_theme": "snow", "night_theme": "snow"},
    75: {"condition": "Snow", "description": "Heavy snow", "day_icon": "extreme-snow-fill", "night_icon": "extreme-snow-fill", "day_theme": "snow", "night_theme": "snow"},
    80: {"condition": "Rain Showers", "description": "Light rain showers", "day_icon": "showers-fill", "night_icon": "showers-fill", "day_theme": "rain", "night_theme": "rain"},
    81: {"condition": "Rain Showers", "description": "Moderate rain showers", "day_icon": "showers-fill", "night_icon": "showers-fill", "day_theme": "rain", "night_theme": "rain"},
    82: {"condition": "Rain Showers", "description": "Violent rain showers", "day_icon": "extreme-rain-fill", "night_icon": "extreme-rain-fill", "day_theme": "storm", "night_theme": "storm"},
    95: {"condition": "Thunderstorm", "description": "Thunderstorm", "day_icon": "thunderstorms-fill", "night_icon": "thunderstorms-fill", "day_theme": "storm", "night_theme": "storm"},
    96: {"condition": "Thunderstorm", "description": "Thunderstorm with hail", "day_icon": "thunderstorms-extreme-fill", "night_icon": "thunderstorms-extreme-fill", "day_theme": "storm", "night_theme": "storm"},
    99: {"condition": "Thunderstorm", "description": "Severe thunderstorm with hail", "day_icon": "thunderstorms-extreme-fill", "night_icon": "thunderstorms-extreme-fill", "day_theme": "storm", "night_theme": "storm"},
}


def icon_url(icon_name):
    return f"https://api.iconify.design/meteocons:{icon_name}.svg"


def weather_meta(code, is_day):
    data = WEATHER_CODE_MAP.get(code, WEATHER_CODE_MAP[0])
    icon_name = data["day_icon"] if is_day else data["night_icon"]
    theme = data["day_theme"] if is_day else data["night_theme"]
    return {
        "condition": data["condition"],
        "description": data["description"],
        "icon_url": icon_url(icon_name),
        "theme": theme,
    }


def geocode_city(city):
    response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results") or []

    if not results:
        raise LookupError("We couldn't find that location. Please try another city.")

    match = results[0]
    return {
        "name": match["name"],
        "country": match.get("country", ""),
        "latitude": match["latitude"],
        "longitude": match["longitude"],
    }


def reverse_lookup(lat, lon):
    response = requests.get(
        REVERSE_GEOCODING_URL,
        params={"latitude": lat, "longitude": lon, "language": "en", "format": "json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results") or []
    match = results[0] if results else {}

    return {
        "name": match.get("name", "Your Location"),
        "country": match.get("country", ""),
        "latitude": lat,
        "longitude": lon,
    }


def normalize_weather(location, payload):
    current = payload["current"]
    current_meta = weather_meta(current["weather_code"], bool(current["is_day"]))

    forecast = []
    for index, date in enumerate(payload["daily"]["time"][:5]):
        code = payload["daily"]["weather_code"][index]
        day_meta = weather_meta(code, True)
        forecast.append(
            {
                "day": date[:10],
                "date": date,
                "temperature": round(payload["daily"]["temperature_2m_max"][index]),
                "feels_like": round(payload["daily"]["apparent_temperature_max"][index]),
                "condition": day_meta["condition"],
                "description": day_meta["description"],
                "icon_url": day_meta["icon_url"],
            }
        )

    return {
        "current": {
            "city": location["name"],
            "country": location["country"],
            "temperature": round(current["temperature_2m"]),
            "condition": current_meta["condition"],
            "description": current_meta["description"],
            "humidity": round(current["relative_humidity_2m"]),
            "wind_speed": round(current["wind_speed_10m"], 1),
            "feels_like": round(current["apparent_temperature"]),
            "icon_url": current_meta["icon_url"],
            "theme": current_meta["theme"],
            "coordinates": {
                "lat": location["latitude"],
                "lon": location["longitude"],
            },
        },
        "forecast": forecast,
    }


def fetch_weather(city=None, lat=None, lon=None):
    if city:
        location = geocode_city(city)
    else:
        location = reverse_lookup(lat, lon)

    forecast_response = requests.get(
        FORECAST_URL,
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code,is_day",
            "daily": "weather_code,temperature_2m_max,apparent_temperature_max",
            "timezone": "auto",
            "forecast_days": 5,
        },
        timeout=REQUEST_TIMEOUT,
    )
    forecast_response.raise_for_status()
    return normalize_weather(location, forecast_response.json())


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/weather")
def get_weather():
    city = request.args.get("city", "").strip()
    lat = request.args.get("lat", "").strip()
    lon = request.args.get("lon", "").strip()

    if not city and not (lat and lon):
        return jsonify({"error": "Please provide a city or coordinates."}), 400

    try:
        data = fetch_weather(city=city or None, lat=lat or None, lon=lon or None)
        return jsonify(data)
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except requests.HTTPError:
        return jsonify({"error": "Weather service request failed. Please try again."}), 502
    except requests.RequestException:
        return jsonify({"error": "Network issue while contacting the weather service."}), 502


if __name__ == "__main__":
    app.run(debug=True)
