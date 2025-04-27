import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def send_test_email():
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    email = EmailMessage()
    email['Subject'] = 'Test Email from Grad2Growth'
    email['From'] = smtp_user
    email['To'] = 'yedward193@gmail.com'  # <-- put your real personal email here
    email.set_content('This is a test email sent from Grad2Growth support email.')

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(email)

if __name__ == "__main__":
    send_test_email()
