import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import logging
import ssl
from crud_api.config import SENDER_EMAIL, SENDER_EMAIL_PASSWORD
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
# SENDER_GMAIL = os.environ["SENDER_GMAIL"]
# SENDER_GMAIL_PASSWORD = os.environ["SENDER_GMAIL_PASSWORD"]
# dirname = os.path.dirname(__file__)
# templates_folder = os.path.join(dirname, '../templates')
logger = logging.getLogger("uvicorn")


conf = ConnectionConfig(
    MAIL_USERNAME = "omrylcn",
    MAIL_PASSWORD = SENDER_EMAIL_PASSWORD,
    MAIL_FROM = SENDER_EMAIL,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="FastAPI forgot password example",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False,
    #TEMPLATE_FOLDER = templates_folder,
)


async def send_reset_password_mail(recipient_email, user, url, expire_in_minutes):
    template_body = {
        "user": user,
        "url": url,
        "expire_in_minutes": expire_in_minutes
    }
    try:
        # message = MessageSchema(
        #     subject="FastAPI forgot password application reset password",
        #     recipients=recipient_email,
        #     template_body=template_body,
        #     subtype=MessageType.html
        # )
        html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """

        message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=[recipient_email],
            body=html,
            subtype=MessageType.html)
        fm = FastMail(conf)
        await fm.send_message(message)#, template_name="reset_password_email.html")
    except Exception as e:
        #logger.error(f"Something went wrong in reset password email")
        logger.error(str(e),exc_info=True)