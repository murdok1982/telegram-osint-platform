import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

logger = logging.getLogger(__name__)


def send_email_with_pdf(case_id: int, risk_score: float, pdf_path: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    receiver = os.getenv("REPORT_RECEIVER")

    if not all([smtp_server, smtp_user, smtp_pass, receiver]):
        logger.info("SMTP configuration missing. Skipping email notification.")
        return

    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = receiver
    msg['Subject'] = f"CTI Alert - Case #{case_id} - Risk {risk_score}"

    body = f"An intelligence case has been generated for a high-risk event (Score: {risk_score}). Please find the attached report."
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(pdf_path)}")
        msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info(f"Email sent successfully for case #{case_id}")
    except Exception as e:
        logger.error(f"Failed to send email for case #{case_id}: {e}")
