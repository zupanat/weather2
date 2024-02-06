from flask import Flask, jsonify
import threading
import requests
import schedule
import time
import os

app = Flask(__name__)


def fetch_weather_and_aqi(lat, lon):
    print(f"Fetching weather and AQI for coordinates {lat}, {lon}...")
    airvisual_url = f'http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key=d7ea92de-7993-4b87-8cb1-a1da9604c5c4'
    response = requests.get(airvisual_url).json()

    # Use .get() to avoid KeyError
    data = response.get('data', {})
    current = data.get('current', {})

    pollution = current.get('pollution', {})
    aqi = pollution.get('aqius', None)

    weather = current.get('weather', {})
    temperature = weather.get('tp', None)
    weather_condition_icon = weather.get('ic', None)

    if aqi and temperature and weather_condition_icon:
        weather_description = get_weather_description(weather_condition_icon)
        print(f"AQI: {aqi}, Temperature: {temperature}°C, Weather: {weather_description}")
        return aqi, temperature, weather_description
    else:
        print("Required data is missing in the API response")
        return None, None, None



def get_weather_description(icon_code):
    descriptions = {
        "01d": "ท้องฟ้าแจ่มใส",
        "01n": "ท้องฟ้าแจ่มใส (กลางคืน)",
        "02d": "เมฆเล็กน้อย",
        "02n": "เมฆเล็กน้อย (กลางคืน)",
        "03d": "เมฆกระจาย",
        "03n": "เมฆกระจาย (กลางคืน)",
        "04d": "เมฆเป็นส่วนมาก",
        "04n": "เมฆเป็นส่วนมาก (กลางคืน)",
        "09d": "ฝนตกเล็กน้อย",
        "09n": "ฝนตกเล็กน้อย (กลางคืน)",
        "10d": "ฝนตก",
        "10n": "ฝนตก (กลางคืน)",
        "11d": "พายุฝนฟ้าคะนอง",
        "11n": "พายุฝนฟ้าคะนอง (กลางคืน)",
        "13d": "หิมะ",
        "13n": "หิมะ (กลางคืน)",
        "50d": "หมอก",
        "50n": "หมอก (กลางคืน)"
    }
    return descriptions.get(icon_code, "สภาพอากาศไม่ทราบ")


def send_notification(location, aqi, temperature, weather_description):
    if aqi is not None and temperature is not None and weather_description is not None:
        print(f"กำลังส่งการแจ้งเตือนสำหรับ {location}...")
        line_notify_token = 'aYiCJJNFez4ctYJ6o0nV9peZkgVivICWjHZFUb5mevl'
        line_url = 'https://notify-api.line.me/api/notify'
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + line_notify_token}
        message = f'{location} สภาพอากาศ: AQI {aqi}, อุณหภูมิ {temperature}°C, {weather_description}'
        data = {'message': message}
        response = requests.post(line_url, headers=headers, data=data)
        if response.status_code == 200:
            print(f"การแจ้งเตือนสำหรับ {location} ส่งสำเร็จ")
        else:
            print(f"ไม่สามารถส่งการแจ้งเตือนสำหรับ {location} ได้ รหัสสถานะ: {response.status_code}")
    else:
        print(f"ไม่มีข้อมูลสำหรับการส่งสำหรับ {location}")


def job():
    print("Starting scheduled job...")

    # Define locations with their latitudes and longitudes
    locations = {
        "Si Racha": (13.1737, 100.9311),
        "Bang Lamung": (12.9276, 100.8771)
    }

    # Loop through each location, fetch weather and AQI, and send notifications
    for location, (lat, lon) in locations.items():
        try:
            aqi, temperature, weather_description = fetch_weather_and_aqi(lat, lon)
            if aqi is not None and temperature is not None and weather_description is not None:
                send_notification(location, aqi, temperature, weather_description)
            else:
                print(f"Failed to fetch data for {location}.")
        except Exception as e:
            print(f"An error occurred for {location}: {e}")

    print("Scheduled job completed.")

def run_scheduler():
    # Run the job immediately the first time the scheduler starts
    job()

    # Then schedule it to run at the start of every hour
    schedule.every().hour.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    return "The scheduler is running. Access /run-job to run the job manually."

@app.route('/run-job')
def run_job():
    try:
        job()
        return jsonify({"success": True, "message": "Job executed successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/healthz')
def healthz():
    # Perform necessary sanity checks here. For simplicity, this example will just return a 200 OK response.
    return "OK", 200

if __name__ == '__main__':
    # Start the scheduler in a background thread
    threading.Thread(target=run_scheduler, daemon=True).start()
    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
