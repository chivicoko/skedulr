import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import datetime
import os
from dotenv import load_dotenv
from logger import setup_logger, log_info, log_debug, log_error

load_dotenv()

# Configure logging
logging.basicConfig(
    filename='daily_report.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

logger =  setup_logger('Daily Report')

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = 'victor.c.okoye@gmail.com'
EMAIL_TO = ['vicharmonic@gmail.com', 'hacura@duck.com']
EMAIL_SUBJECT = 'Daily Report'

def gather_report_data():
    log_info(logger, "Gathering report data...")
    # logger.info("Gathering report data.")
    # Placeholder function to simulate report data gathering
    report_data = "This is the daily report content."
    log_debug(logger, f"Report data gathered: {report_data}")
    # logger.debug(f"Report data gathered: {report_data}")
    return report_data

def send_email(subject, body, to_addresses):
    log_info(logger, "Preparing to send email...")
    # logger.info("Preparing to send email.")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = ', '.join(to_addresses)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, to_addresses, msg.as_string())
        server.quit()
        log_info(logger, "Email sent successfully.")
        # logger.info("Email sent successfully.")
    except Exception as e:
        log_error(logger, f"Failed to send email. Error: {e}")
        # logger.error(f"Failed to send email. Error: {e}")

def job():
    try:
        log_info(logger, f"Job started at {datetime.datetime.now()}")
        # logger.info(f"Job started at {datetime.datetime.now()}")
        report_data = gather_report_data()
        send_email(EMAIL_SUBJECT, report_data, EMAIL_TO)
        log_info(logger, f"Job completed at {datetime.datetime.now()}")
        # logger.info(f"Job completed at {datetime.datetime.now()}")
    except Exception as e:
        log_error(logger, f"Job failed. Error: {e}")
        # logger.error(f"Job failed. Error: {e}")

# Schedule the job every day at a specific time
schedule.every().day.at("09:03").do(job)

log_info(logger, "Scheduler started. Waiting for the scheduled time...")
# print("Scheduler started. Waiting for the scheduled time...")
while True:
    schedule.run_pending()
    time.sleep(1)
