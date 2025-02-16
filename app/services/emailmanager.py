from flask import render_template
from app.models import User
import smtplib
from email.mime.text import MIMEText

class EmailManager:
    @staticmethod
    def send_email(user : User, template: str, alert: float = None):
        html_content = render_template(template, user_name=user.name, amount=alert)
        sender_email = "test@example.com"
        receiver_email = "recipient@example.com"
        message = MIMEText(html_content, "html")
        message["Subject"] = "MailHog Test"
        message["From"] = sender_email
        message["To"] = receiver_email

        try:
            with smtplib.SMTP("smtp", 1025) as server:
                server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")