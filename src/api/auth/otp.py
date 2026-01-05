from email.message import EmailMessage
import aiosmtplib
import random
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_GMAIL_HOST = "smtp.gmail.com"
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_GMAIL_USER")
SMTP_PASS = os.getenv("SMTP_GMAIL_PASS")

def generate_otp():
    return f"{random.randint(100000, 999999)}"

async def send_otp(email_to: str, code: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = email_to
    message["Subject"] = "Your OTP Code"
    message.set_content(f"Your OTP code is: {code}")

    await aiosmtplib.send(message, hostname=SMTP_GMAIL_HOST, port=SMTP_PORT, username=SMTP_USER, password=SMTP_PASS, start_tls=True)
