import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

# Logo en base64 (extrait du logo stylisé dark cyber fourni)
LOGO_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAACaCAYAAABc+dUMAAAABHNCSVQICAgIfAhkiAAABpFJREFUeJzt3Y1y2kYUBeC3NB8DKy0DsQ3MJsA3MAczq6xwC5wE/gfUO8hzcmrDBKUkzQdYi33HcOWe9dWrN5OS5+8lrXH7yXadXt+qvXtQMAAAAAAAAAAAAAAAAAAAAAAAAAAAD8pu4HmWTEN2xuo/1MF8y8wnJ9yk91/N8z69/wN/veaz6yGE2PLoOSZC5jknNuW5+gxbiWBjCPuwDGlTfnzkvsX+gQ9WffZlRv/A06Vc0BvAfPbmgj8tfesWcf0Ln3zPvmccD54ff+4TYzYZYANnFtCWGZYGkWYb/PEaTz4oyMmZyGBkZmubtQPA+WZnZ6eMbEQMx7vwOUhN+YvJjtrvN38rdiYyNZmZq3POaAYLGZmamZkg+4bJzNWZmdkKx/z2oSDl9R/m39c38u8kRmZtZmZrx+YiAzDm/UDsHdPYuyvKc/+YhvVW5E9DYv9u9YMxMzNzIzMMY/nvZjeW/Nsf+T5yGBkZmubtwPA+WFmZmZmTgR/2nWZmZmRux4yMmZyGBkZmubtQPA+WZmZ+SKW8ZB6ZsAGZ3NmZmZmRpZrcsDQGVpDmZmZmRq4/LNzN1f3M3M7cwFYkZGZuYmLQOd+VbRKTNmZmZ2Y+E2zIXZQdmZmZm5ggpgLGZmZkZ8ShcxM7OzMzOH8TswczMzszMzh2xbL58AAAAAAAAAAAAAAAAAAAAAAAAAAID7Rf8Bydu8uTFzo1YAAAAASUVORK5CYII="


def send_validation_email(to_email: str, code: str):
    msg = EmailMessage()
    msg["Subject"] = "Validez votre compte TypingSpeedApp"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    # Texte brut de secours
    msg.set_content(f"Voici votre code de validation : {code}")

    # HTML stylisé en thème dark / cyber
    html = f"""
    <html>
    <body style='font-family: "Segoe UI", sans-serif; background-color: #0f172a; padding: 30px; color: #e2e8f0;'>
      <div style='max-width: 600px; margin: auto; background-color: #1e293b; border-radius: 12px; padding: 40px; box-shadow: 0 0 25px rgba(0,255,255,0.15); border: 1px solid #334155;'>
        <div style='text-align: center;'>
          <img src='{LOGO_BASE64}' alt='TypingSpeedApp' style='height: 60px; margin-bottom: 30px; filter: drop-shadow(0 0 5px #38bdf8);'>
          <h2 style='color: #38bdf8; text-transform: uppercase; letter-spacing: 1px;'>Validation de compte</h2>
          <p style='font-size: 16px; color: #cbd5e1; margin: 20px 0;'>Bienvenue sur <strong>TypingSpeedApp</strong>. Pour finaliser votre inscription, veuillez entrer le code suivant :</p>
          <div style='font-size: 30px; font-weight: bold; margin: 25px 0; color: #0ea5e9; letter-spacing: 4px; background: #0f172a; padding: 12px 24px; border-radius: 8px; border: 1px dashed #38bdf8; display: inline-block;'>
            {code}
          </div>
          <p style='font-size: 14px; color: #94a3b8; margin-top: 24px;'>Ce code est temporaire. Ne le communiquez à personne.</p>
        </div>
        <hr style='margin: 40px 0; border: none; border-top: 1px solid #334155;'>
        <div style='text-align: center; font-size: 12px; color: #64748b;'>
          TypingSpeedApp • Sécurisé et rapide — 2025
        </div>
      </div>
    </body>
    </html>
    """
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)


def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)


def send_reset_email(email: str, temp_password: str):
    msg = EmailMessage()
    msg["Subject"] = "Réinitialisation de votre mot de passe"
    msg["From"] = FROM_EMAIL
    msg["To"] = email

    msg.set_content(f"Voici votre mot de passe temporaire : {temp_password}")

    html = f"""
    <html>
    <body style='font-family: "Segoe UI", sans-serif; background-color: #0f172a; padding: 30px; color: #e2e8f0;'>
      <div style='max-width: 600px; margin: auto; background-color: #1e293b; border-radius: 12px; padding: 40px; box-shadow: 0 0 25px rgba(0,255,255,0.15); border: 1px solid #334155;'>
        <div style='text-align: center;'>
          <img src='{LOGO_BASE64}' alt='TypingSpeedApp' style='height: 60px; margin-bottom: 30px; filter: drop-shadow(0 0 5px #38bdf8);'>
          <h2 style='color: #38bdf8; text-transform: uppercase; letter-spacing: 1px;'>Réinitialisation de mot de passe</h2>
          <p style='font-size: 16px; color: #cbd5e1; margin: 20px 0;'>Voici votre mot de passe temporaire pour accéder à votre compte :</p>
          <div style='font-size: 26px; font-weight: bold; margin: 20px 0; color: #0ea5e9; background: #0f172a; padding: 12px 24px; border-radius: 8px; border: 1px dashed #38bdf8; display: inline-block;'>
            {temp_password}
          </div>
          <p style='font-size: 14px; color: #94a3b8; margin-top: 24px;'>Ce mot de passe est valable 5 minutes. Une fois connecté, vous serez invité à en choisir un nouveau.</p>
        </div>
        <hr style='margin: 40px 0; border: none; border-top: 1px solid #334155;'>
        <div style='text-align: center; font-size: 12px; color: #64748b;'>
          TypingSpeedApp • Sécurisé et rapide — 2025
        </div>
      </div>
    </body>
    </html>
    """
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)
