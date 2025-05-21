import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email, code):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = os.getenv("GMAIL_USERNAME")
        smtp_password = os.getenv("GMAIL_APP_PASSWORD")

        if not smtp_username or not smtp_password:
            print("SMTP credentials not found in environment variables.")
            return False

        subject = "Your Email Verification Code"
        body = f"""
        Hello,

        Thank you for signing up. Please use the following code to verify your email address:

        🔐 Verification Code: {code}

        This code is valid for the next 10 minutes.

        If you did not request this, you can ignore this message.

        -- Your App Team
        """

        message = MIMEMultipart()
        message["From"] = smtp_username
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        print(f"Verification email sent to {email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
