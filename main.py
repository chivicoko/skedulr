import sys
import smtplib
import schedule
import time
import os
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QTextEdit, QPushButton, QLabel, QTimeEdit, QTextBrowser, QFormLayout, QSizePolicy
)
from PyQt5.QtCore import QThread, pyqtSignal, QTime
from dotenv import load_dotenv
from logger import setup_logger, log_info, log_debug, log_error, log_success, log_failed, log_warning

load_dotenv()

logger = setup_logger('Life Quotes')

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')

quotes = [
    "The best way to predict the future is to invent it. - Alan Kay",
    "Life is 10% what happens to us and 90% how we react to it. - Charles R. Swindoll",
    "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
    "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
    "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb",
    "You miss 100% of the shots you don't take. - Wayne Gretzky",
    "I am not a product of my circumstances. I am a product of my decisions. - Stephen R. Covey",
    "Every strike brings me closer to the next home run. - Babe Ruth",
    "Life is what happens when you're busy making other plans. - John Lennon",
    "The only way to do great work is to love what you do. - Steve Jobs",
]

class EmailScheduler(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.email_to = []
        self.email_subject = ''
        self.email_body = ''
        self.scheduled_time = QTime.currentTime()
        self.running = False
        self.email_sent_successfully = False

    def get_data(self):
        try:
            log_info(logger, "Getting data...")
            self.email_body = random.choice(quotes)
            log_debug(logger, f"Data gotten: {self.email_body}")
            return self.email_body
        except Exception as e:
            log_error(logger, f"Failed to get data. Error: {e}")
            self.log_signal.emit(f'<div style="color:red;">[{datetime.now().strftime("%H:%M:%S")}] [FAILURE] Failed to get data. Error: {e}</div>')
            raise

    def send_email(self, subject, body, to_addresses):
        log_info(logger, "Preparing to send email...")
        self.log_signal.emit(f'<div style="color:black;">[{datetime.now().strftime("%H:%M:%S")}] [INFO] Preparing to send email...</div>')
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        retries = 3
        for attempt in range(retries):
            try:
                log_info(logger, f"Attempting to send email, try {attempt + 1} of {retries}...")
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(EMAIL_FROM, to_addresses, msg.as_string())
                server.quit()
                log_success(logger, "Email sent successfully.")
                self.log_signal.emit(f'<div style="color:green;">[{datetime.now().strftime("%H:%M:%S")}] [SUCCESS] Email sent successfully.</div>')
                return True
            except smtplib.SMTPConnectError as e:
                log_warning(logger, f"Network issue on attempt {attempt + 1} of {retries}: {e}")
                self.log_signal.emit(f'<div style="color:orange;">[{datetime.now().strftime("%H:%M:%S")}] [WARNING] Network issue on attempt {attempt + 1} of {retries}: {e}</div>')
            except smtplib.SMTPException as e:
                log_error(logger, f"SMTP error on attempt {attempt + 1} of {retries}: {e}")
                self.log_signal.emit(f'<div style="color:orange;">[{datetime.now().strftime("%H:%M:%S")}] [WARNING] SMTP error on attempt {attempt + 1} of {retries}: {e}</div>')
            except Exception as e:
                log_error(logger, f"Unexpected error on attempt {attempt + 1} of {retries}: {e}")
                self.log_signal.emit(f'<div style="color:orange;">[{datetime.now().strftime("%H:%M:%S")}] [WARNING] Unexpected error on attempt {attempt + 1} of {retries}: {e}</div>')
            time.sleep(5)

        log_error(logger, "Failed to send email after multiple attempts.")
        self.log_signal.emit(f'<div style="color:red;">[{datetime.now().strftime("%H:%M:%S")}] [FAILURE] Failed to send email after multiple attempts.</div>')
        return False

    def run(self):
        self.running = True
        schedule.every().day.at(self.scheduled_time.toString('HH:mm')).do(self.job)
        self.log_signal.emit(f'<div style="color:black;">[{datetime.now().strftime("%H:%M:%S")}] [INFO] Scheduler started. Waiting for the scheduled time... {self.scheduled_time.toString("HH:mm")}</div>')
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        self.log_signal.emit(f'<div style="color:black;">[{datetime.now().strftime("%H:%M:%S")}] [INFO] Scheduler stopped.')
        self.log_signal.emit(f'********************************************************** \n')
        log_info(logger, "Scheduler stopped. \n ********************************************************** \n")
    
    def job(self):
        try:
            log_info(logger, f"Job started at {datetime.now()}")
            self.log_signal.emit(f'<div style="color:black;">[{datetime.now().strftime("%H:%M:%S")}] [INFO] Job started at {datetime.now()}</div>')
            
            self.email_sent_successfully = False

            all_data = self.get_data()
            if not self.email_subject:
                self.email_subject = "Life's Good! Tomorrow is Pregnant!"

            if not self.email_sent_successfully:
                if self.send_email(self.email_subject, all_data, self.email_to):
                    self.email_sent_successfully = True
                    log_info(logger, f"Job completed successfully at {datetime.now()}")
                    self.log_signal.emit(f'<div style="color:green;">[{datetime.now().strftime("%H:%M:%S")}] [SUCCESS] Job completed successfully at {datetime.now()}</div>')
                else:
                    log_failed(logger, f"Job failed to send email at {datetime.now()}")
                    self.log_signal.emit(f'<div style="color:red;">[{datetime.now().strftime("%H:%M:%S")}] [FAILURE] Job failed to send email at {datetime.now()}</div>')
            else:
                log_info(logger, "Job already completed successfully for this scheduled time.")
        except Exception as e:
            log_error(logger, f"Job failed. Error: {e}")
            self.log_signal.emit(f'<div style="color:red;">[{datetime.now().strftime("%H:%M:%S")}] [FAILURE] Job failed. Error: {e}</div>')


class EmailSchedulerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.scheduler_thread = EmailScheduler()
        self.scheduler_thread.log_signal.connect(self.update_log)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Skedulr')
        self.setFixedSize(900, 700)

        main_layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.subject_input = QLineEdit()
        form_layout.addRow("Subject:", self.subject_input)

        self.body_input = QTextEdit()
        self.body_input.setMinimumHeight(230)
        form_layout.addRow("Body:", self.body_input)

        email_time_layout = QHBoxLayout()

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Enter recipient email(s), separated by commas")
        email_time_layout.addWidget(self.recipient_input, 90)

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        email_time_layout.addWidget(self.time_input, 10)
        form_layout.addRow("Recipient & Time:", email_time_layout)

        button_layout = QHBoxLayout()
        start_btn = QPushButton("Start Scheduler")
        start_btn.clicked.connect(self.start_scheduler)
        stop_btn = QPushButton("Stop Scheduler")
        stop_btn.clicked.connect(self.stop_scheduler)
        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)

        self.log_output = QTextBrowser()
        self.log_output.setStyleSheet(f'padding:0px;')
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_output.setAcceptRichText(True)
        self.log_output.setOpenExternalLinks(True)
        log_label = QLabel("Logs:")

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_output, stretch=1)

        self.setLayout(main_layout)

        self.setFixedSize(self.size())

    def start_scheduler(self):
        self.scheduler_thread.email_subject = self.subject_input.text()
        self.scheduler_thread.email_body = self.body_input.toPlainText()

        recipients = self.recipient_input.text().split(',')
        self.scheduler_thread.email_to = [email.strip() for email in recipients]

        self.scheduler_thread.scheduled_time = self.time_input.time()
        log_info(logger, "Starting scheduler...")
        self.scheduler_thread.start()

    def stop_scheduler(self):
        self.scheduler_thread.stop()

    def update_log(self, message):
        self.log_output.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = EmailSchedulerGUI()
    gui.show()
    sys.exit(app.exec_())
