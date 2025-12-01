import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from openai import OpenAI

from db import init_db, SessionLocal, Farmer
from weather import get_weather_by_city
from scheduler import start_scheduler

load_dotenv()

app = Flask(__name__)
init_db()

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Twilio WhatsApp number
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")

# ------------------ Helpers ------------------

def get_or_create_farmer(phone):
    db = SessionLocal()
    try:
        farmer = db.query(Farmer).filter(Farmer.phone == phone).first()
        if not farmer:
            farmer = Farmer(phone=phone)
            db.add(farmer)
            db.commit()
            db.refresh(farmer)
        return farmer
    finally:
        db.close()


def ai_generate_reply(district, crop=None):
    weather = get_weather_by_city(district)

    prompt = f"""
You are an AI agricultural assistant for farmers in Bangladesh.

Give response in BOTH:
1) Bengali
2) English

District: {district}
Crop: {crop if crop else "Not specified"}
Weather data: {weather}

Provide:
- Current weather summary
- Drought risk (High/Medium/Low)
- Water-saving tips
- Crop protection advice
- Weekly suggestion for farmers

Keep it short and simple. Use bullet points.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a smart agricultural AI advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.4
    )

    return response.choices[0].message.content


# ------------------ Routes ------------------

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/sms", methods=["POST"])
def sms_webhook():

    incoming = request.form.get("Body", "").strip()
    from_raw = request.form.get("From", "")

    resp = MessagingResponse()
    msg = resp.message()

    if not from_raw:
        msg.body("Sender not detected.")
        return str(resp)

    if from_raw.startswith("whatsapp:"):
        from_number = from_raw.replace("whatsapp:", "")
    else:
        from_number = from_raw

    text = incoming.lower()

    if text == "help":
        msg.body(
            """
🌾 Krishi AI Assistant

Commands:
1. Send your district name: Rajshahi
2. Send: district + crop → Rajshahi paddy
3. register Rajshahi paddy → Weekly alerts
4. stop → Unsubscribe

Replies in Bengali & English
"""
        )
        return str(resp)

    if text.startswith("register"):
        parts = text.split()
        if len(parts) >= 2:
            district = parts[1]
            crop = parts[2] if len(parts) >= 3 else None

            db = SessionLocal()
            farmer = db.query(Farmer).filter(Farmer.phone == from_number).first()

            if farmer:
                farmer.district = district
                farmer.crop = crop
            else:
                farmer = Farmer(phone=from_number, district=district, crop=crop)
                db.add(farmer)

            db.commit()
            db.close()

            msg.body(
                f"""✅ Registration Success

District: {district}
Crop: {crop if crop else "Not given"}

You will receive AI weekly alerts 📢
"""
            )
        else:
            msg.body("Correct format: register <district> <crop>")

        return str(resp)

    if text == "stop":
        db = SessionLocal()
        farmer = db.query(Farmer).filter(Farmer.phone == from_number).first()
        if farmer:
            db.delete(farmer)
            db.commit()
            msg.body("You are successfully unsubscribed.")
        else:
            msg.body("You were not registered.")
        db.close()
        return str(resp)

    # Normal AI message
    parts = text.split()
    district = parts[0]
    crop = parts[1] if len(parts) > 1 else None

    get_or_create_farmer(from_number)

    try:
        reply = ai_generate_reply(district, crop)
        msg.body(reply)
    except Exception as e:
        msg.body("⚠️ AI service temporarily unavailable. Please try again later.")

    return str(resp)


if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
