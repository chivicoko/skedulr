import sys
import smtplib
import schedule
import time
import os
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

# Set up logger
logger = setup_logger('Daily Report')

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')

class EmailScheduler(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.email_to = []
        self.email_subject = ''
        self.email_body = ''
        self.scheduled_time = QTime.currentTime()
        self.running = False
        self.email_sent_successfully = False  # Flag to track successful email attempt

    def gather_report_data(self):
        try:
            log_info(logger, "Gathering report data...")
            report_data = self.email_body
            log_debug(logger, f"Report data gathered: {report_data}")
            return report_data
        except Exception as e:
            log_error(logger, f"Failed to gather report data. Error: {e}")
            self.log_signal.emit(f'<div style="color:red;">[{datetime.now().strftime("%H:%M:%S")}] [FAILURE] Failed to gather report data. Error: {e}</div>')
            raise

    def send_email(self, subject, body, to_addresses):
        if self.email_sent_successfully:  # Check if email already sent successfully
            log_info(logger, "Email already sent successfully for this scheduled time.")
            return True

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
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(EMAIL_FROM, to_addresses, msg.as_string())
                server.quit()
                self.email_sent_successfully = True  # Set flag to True if email sent successfully
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
        self.log_signal.emit(f'____**********************************************************____ \n')
        log_info(logger, "Scheduler stopped. \n ____**********************************************************____ \n")
    
    def job(self):
        try:
            log_info(logger, f"Job started at {datetime.now()}")
            self.log_signal.emit(f'<div style="color:black;">[{datetime.now().strftime("%H:%M:%S")}] [INFO] Job started at {datetime.now()}</div>')
            report_data = self.gather_report_data()
            if not self.email_sent_successfully:  # Check if email already sent successfully
                if self.send_email(self.email_subject, report_data, self.email_to):
                    self.email_sent_successfully = True  # Set flag to True upon successful email attempt
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
        self.setWindowTitle('Email Scheduler')
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
