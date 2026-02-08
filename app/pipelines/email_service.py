"""
Email Service Module

Handles sending email notifications for alerts.
Configured to use Gmail SMTP with App Password authentication.

To configure:
1. Update EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECEIVER below
2. For Gmail, generate an App Password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Email Configuration - Use environment variables for deployment
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "adabbawa10@gmail.com")  # Sender email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "ccgfdsohymdvgixw")     # Gmail App Password (not regular password)
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "adabbawa06@gmail.com")  # Recipient email address

def send_email(subject, body):
    """
    Send email alert notification.
    
    Args:
        subject: Email subject line
        body: Email body content
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        
        # Add body with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_body = f"""
Alert Notification
==================

Time: {timestamp}

{body}

---
This is an automated alert from the Surveillance System.
"""
        msg.attach(MIMEText(email_body, "plain"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent successfully: {subject}")
            
    except smtplib.SMTPAuthenticationError:
        print(f"ERROR: Email authentication failed. Check email credentials.")
    except smtplib.SMTPException as e:
        print(f"ERROR: Failed to send email: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error sending email: {e}")
