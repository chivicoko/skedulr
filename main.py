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

logger = setup_logger('Daily Report')

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = 'victor.c.okoye@gmail.com'
EMAIL_TO = ['vicharmonic@gmail.com', 'hacura@duck.com']
EMAIL_SUBJECT = 'Daily Report'

def gather_report_data():
    try:
        log_info(logger, "Gathering report data...")
        report_data = "This is the daily report content."
        log_debug(logger, f"Report data gathered: {report_data}")
        return report_data
    except Exception as e:
        log_error(logger, f"Failed to gather report data. Error: {e}")
        raise

def send_email(subject, body, to_addresses):
    log_info(logger, "Preparing to send email...")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = ', '.join(to_addresses)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    retries = 3
    for attempt in range(retries):
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_addresses, msg.as_string())
            server.quit()
            log_info(logger, "Email sent successfully.")
            return
        except smtplib.SMTPException as e:
            log_error(logger, f"SMTP error on attempt {attempt + 1} of {retries}: {e}")
        except Exception as e:
            log_error(logger, f"Unexpected error on attempt {attempt + 1} of {retries}: {e}")
        time.sleep(5)

    log_error(logger, "Failed to send email after multiple attempts.")

def job():
    try:
        log_info(logger, f"Job started at {datetime.datetime.now()}")
        report_data = gather_report_data()
        send_email(EMAIL_SUBJECT, report_data, EMAIL_TO)
        log_info(logger, f"Job completed at {datetime.datetime.now()} \n =====**************************************************===== \n\n")
    except Exception as e:
        log_error(logger, f"Job failed. Error: {e}")

schedule.every().day.at("14:42").do(job)

log_info(logger, "Scheduler started. Waiting for the scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(1)
