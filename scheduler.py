import os
import time
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from db import SessionLocal, Farmer
from weather import get_weather_by_city
from twilio.rest import Client

load_dotenv()

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)


def build_ai_message(farmer):

    weather = get_weather_by_city(farmer.district)

    prompt = f"""
Weekly farming alert in Bengali and English

District: {farmer.district}
Crop: {farmer.crop}
Weather: {weather}

Include:
- rainfall outlook
- drought risk
- water management
- crop care
"""

    response = client_ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.4
    )

    return response.choices[0].message.content


def send_weekly_updates():
    db = SessionLocal()
    farmers = db.query(Farmer).all()

    for farmer in farmers:
        try:
            msg = build_ai_message(farmer)

            client.messages.create(
                body=msg,
                from_=TWILIO_WHATSAPP,
                to=f"whatsapp:{farmer.phone}"
            )

            time.sleep(1)

        except Exception as e:
            print("Error:", e)

    db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_weekly_updates, "interval", days=7)
    scheduler.start()
    return scheduler
