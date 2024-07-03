import smtplib
from email.mime.text import MIMEText

def send_local_email(sender_email, receiver_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent to local server successfully!")
    except Exception as e:
        print(f"Error: {e}")


