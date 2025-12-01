🌦️ ClimateBot – SMS Weather & Drought Alert System

Automated SMS bot that sends weather updates, drought alerts, and smart climate tips using Flask, Twilio, OpenAI, and APScheduler.

🚀 Features

📩 SMS Weather Updates – Users receive real-time weather reports.

🔔 Daily Automated Alerts – Scheduler sends morning drought tips + weather.

🧠 AI Smart Responses – OpenAI generates helpful climate-friendly suggestions.

🌡️ Weather API Integration – Fetches live temperature, humidity, rainfall.

💾 SQLite Database – Stores user phone numbers and subscription info.

🛠️ Easy Deployment – Ready for Render/Heroku setup using Gunicorn.

🏗️ Tech Stack
Tool / Library	Purpose
Flask	Backend API + Webhook for Twilio
Twilio	Sends & receives SMS messages
OpenAI API	Generates intelligent climate tips
APScheduler	Schedules automatic daily messages
SQLAlchemy	Database ORM (SQLite)
Requests	Calls Weather API
Gunicorn	Production WSGI server
python-dotenv	Loads environment variables
Ngrok (optional)	Exposes local server for Twilio testing
📦 Installation

Clone the repo:

git clone https://github.com/yogi941/CLIMATEBOT.git
cd CLIMATEBOT


Install dependencies:

pip install -r requirements.txt

🔐 Environment Variables (.env)

Create a .env file and add your secrets (Do NOT commit this file):

TWILIO_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=+1xxxxxxxxxx

OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY=your_weather_api_key

DATABASE_URL=sqlite:///drought_bot.db


Be sure .env is in .gitignore.

▶️ Run Project

Start Flask app:

python app.py


Or with Gunicorn (for deployment):

gunicorn app:app

🛰️ Using Ngrok for Local SMS Testing

Expose local server:

ngrok http 5000


Copy the HTTPS URL and paste it into:
Twilio → Console → Phone Numbers → Webhook → Messaging Webhook URL

Example:

https://1234abcd.ngrok.io/sms

⏱️ Scheduler (Automatic Messages)

APScheduler automatically sends messages once a day.
Runs from scheduler.py.

📁 Project Structure
CLIMATEBOT/
│── app.py             # Flask server + Twilio webhook
│── weather.py         # Weather API handler
│── ai.py              # OpenAI response generator
│── tips.py            # Drought tips list
│── scheduler.py       # Daily message scheduler
│── db.py              # SQLAlchemy DB models
│── drought_bot.db     # SQLite database
│── requirements.txt
│── Procfile
│── runtime.txt
│── .gitignore

📬 Example SMS Flow

User: “weather chennai”
Bot: “Temperature 31°C, humidity 70%, no rainfall expected today.”

User: “tip”
Bot (AI): “To save water, collect AC water for plant watering.”

🌐 Deployment (Render/Heroku)

Add your environment variables

Use Procfile for auto start:

web: gunicorn app:app

🤝 Contributing

Pull requests are welcome!
