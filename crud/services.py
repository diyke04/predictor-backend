from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from models.services import TaskStatus
from utils.send_mail import send_local_email

class EmailSettings(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    MAIL_STARTTLS:bool

email_settings = EmailSettings(
    MAIL_USERNAME="predictor@fastmail.com",
    MAIL_PASSWORD="5d5m12b272",
    MAIL_FROM="iykedave04@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    MAIL_STARTTLS= True,
)

conf = ConnectionConfig(
    MAIL_USERNAME ="iykedave04@gmail.com",
    MAIL_PASSWORD = "5d5m12b272",
    MAIL_FROM = "iykedave04@gmail.com",
    #MAIL_PORT = 465,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    #MAIL_STARTTLS = False,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# FastAPI-Mail instance
fastmail = FastMail(conf)




async def send_email(subject: str, recipients: List[EmailStr], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html"
    )
    await fastmail.send_message(message)



async def update_task_status(db: AsyncSession, task_id: str, status: str):
    
    task_status = await db.get(TaskStatus, task_id)
    if task_status:
        task_status.status = status
        
        # Send an email notification to the admin
        admin_email = "iykedave04@gmail.com"
        subject = f"Task {task_id} Status Update"
        body = f"The task with ID {task_id} has {status}."
        send_local_email(sender_email="iyke04@gmail.com",
                         receiver_email=admin_email,
                         subject=subject,
                         body=body
                         )
    else:
        task_status = TaskStatus(task_id=task_id, status=status)
        db.add(task_status)

    await db.commit()


