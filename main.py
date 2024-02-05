import requests
import schedule
import time


def fetch_weather_and_aqi(lat, lon):
    print(f"กำลังดึงข้อมูลสภาพอากาศและ AQI สำหรับพิกัด {lat}, {lon}...")
    airvisual_url = f'http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key=d7ea92de-7993-4b87-8cb1-a1da9604c5c4'
    response = requests.get(airvisual_url).json()
    if 'data' in response:
        aqi = response['data']['current']['pollution']['aqius']
        temperature = response['data']['current']['weather']['tp']
        weather_condition_icon = response['data']['current']['weather']['ic']
        weather_description = get_weather_description(weather_condition_icon)
        print(f"AQI: {aqi}, อุณหภูมิ: {temperature}°C, สภาพอากาศ: {weather_description}")
        return aqi, temperature, weather_description
    else:
        print("ไม่สามารถดึงข้อมูลได้")
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
    print("เริ่มต้นงาน...")
    # Si Racha
    si_racha_aqi, si_racha_temperature, si_racha_weather = fetch_weather_and_aqi(13.1737, 100.9311)
    send_notification("ศรีราชา", si_racha_aqi, si_racha_temperature, si_racha_weather)

    # Bang Lamung
    bang_lamung_aqi, bang_lamung_temperature, bang_lamung_weather = fetch_weather_and_aqi(12.9276, 100.8771)
    send_notification("บางละมุง", bang_lamung_aqi, bang_lamung_temperature, bang_lamung_weather)


# ทำงานทันทีเพื่อทดสอบ จากนั้นกำหนดตารางเวลาทุกๆ ชั่วโมง
job()
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)