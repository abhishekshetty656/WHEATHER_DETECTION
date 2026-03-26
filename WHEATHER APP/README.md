# Atmos Weather

A modern, responsive weather application built with Flask, HTML, CSS, and JavaScript. It displays live weather details, dynamic weather-aware backgrounds, and a 5-day forecast using the free Open-Meteo APIs, so it works without requiring an API key.

## Features

- Search weather by city name
- Auto-detect current location with browser geolocation
- Real-time weather metrics including temperature, feels like, humidity, and wind speed
- Dynamic weather icons and adaptive backgrounds
- 5-day forecast cards
- Loading state, smooth transitions, and error handling
- No API key required for the default setup

## Project Structure

```text
WHEATHER APP/
|-- app.py
|-- requirements.txt
|-- README.md
|-- templates/
|   `-- index.html
`-- static/
    |-- style.css
    `-- script.js
```

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Start the Flask application:

```powershell
python app.py
```

4. Open `http://127.0.0.1:5000` in your browser.

## Notes

- Wind speed is displayed in km/h.
- City search uses Open-Meteo geocoding and weather forecast endpoints.

## VS Code Tips

- Open the project folder in Visual Studio Code.
- Select the virtual environment interpreter from the Command Palette.
- Run `python app.py` in the integrated terminal.
