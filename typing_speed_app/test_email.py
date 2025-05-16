import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

print("USER:", os.getenv("SMTP_USER"))
print("PASS:", os.getenv("SMTP_PASS"))


msg = EmailMessage()
msg["Subject"] = "✅ Test d'envoi via Mailjet"
msg["From"] = os.getenv("FROM_EMAIL")
msg["To"] = "parhylfoadjo@gmail.com"
msg.set_content("Bonjour ! Ceci est un test d’envoi SMTP depuis FastAPI avec Mailjet.")

with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as smtp:
    smtp.starttls()
    smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
    smtp.send_message(msg)
