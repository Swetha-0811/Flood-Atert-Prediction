# flood_alert_system/app.py
from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)

# You can set your API key here directly or through environment variable
WEATHER_API_KEY = "7303aa26e93e6857142efb84a5119afb"

# Real weather-based flood risk logic using OpenWeatherMap

def predict_flood_risk(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        rain = data.get('rain', {}).get('1h', 0)  # mm rain in last 1 hour
        humidity = data.get('main', {}).get('humidity', 0)
        temp = data.get('main', {}).get('temp', 0)
        weather_desc = data.get('weather', [{}])[0].get('description', 'Unknown')

        # Simple logic
        if rain > 20 or (rain > 10 and humidity > 80):
            risk = "High"
            prob = 0.9
        elif rain > 5 or humidity > 70:
            risk = "Moderate"
            prob = 0.6
        else:
            risk = "Low"
            prob = 0.2

        return prob, risk, temp, humidity, rain, weather_desc

    except Exception as e:
        # fallback risk if weather API fails
        return 0.5, "Moderate", 0, 0, 0, "Unavailable"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')

    prob, risk, temp, humidity, rain, weather_desc = predict_flood_risk(lat, lon)

    tips = {
        "Low": "Stay aware. Monitor local news for weather updates.",
        "Moderate": "Prepare emergency kit and evacuation plan. Avoid low-lying areas.",
        "High": "Evacuate immediately if advised. Move to higher ground. Avoid flood waters."
    }

    return jsonify({
        'latitude': lat,
        'longitude': lon,
        'probability': round(prob, 2),
        'risk_level': risk,
        'safety_tip': tips[risk],
        'temperature': temp,
        'humidity': humidity,
        'rainfall': rain,
        'weather_condition': weather_desc
    })

if __name__ == '__main__':
    app.run(debug=True)