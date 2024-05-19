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
# from logger import setup_logger, log_info, log_debug, log_error
from logger import setup_logger, log_info, log_debug, log_error, log_success, log_failed


load_dotenv()

# vicharmonic@gmail.com,hacura@gmail.com,vemmace@gmail.com

# Set up logger
logger = setup_logger('Daily Report')

# Load SMTP credentials from .env file
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = 'victor.c.okoye@gmail.com'

class EmailScheduler(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.email_to = []
        self.email_subject = ''
        self.email_body = ''
        self.scheduled_time = QTime.currentTime()
        self.running = False

    def gather_report_data(self):
        try:
            log_info(logger, "Gathering report data...")
            report_data = self.email_body
            log_debug(logger, f"Report data gathered: {report_data}")
            return report_data
        except Exception as e:
            log_error(logger, f"Failed to gather report data. Error: {e}")
            self.log_signal.emit(f"Failed to gather report data. Error: {e}")
            # self.add_output("ERROR", f"Failed to gather report data. Error: {e}")
            raise

    def send_email(self, subject, body, to_addresses):
        log_info(logger, "Preparing to send email...")
        self.log_signal.emit("Preparing to send email...")
        # self.add_output("INFO", f"Preparing to send email...")
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
                self.log_signal.emit("Email sent successfully.")
                # self.add_output("SUCCESS", "Email sent successfully.")
                return
            except smtplib.SMTPException as e:
                log_error(logger, f"SMTP error on attempt {attempt + 1} of {retries}: {e}")
                self.log_signal.emit(f"SMTP error on attempt {attempt + 1} of {retries}: {e}")
                # self.add_output("WARNING", f"SMTP error on attempt {attempt + 1} of {retries}: {e}")
            except Exception as e:
                log_error(logger, f"Unexpected error on attempt {attempt + 1} of {retries}: {e}")
                self.log_signal.emit(f"Unexpected error on attempt {attempt + 1} of {retries}: {e}")
                # self.add_output("WARNING", f"Unexpected error on attempt {attempt + 1} of {retries}: {e}")
            time.sleep(5)

        log_error(logger, "Failed to send email after multiple attempts.")
        self.log_signal.emit("Failed to send email after multiple attempts.")
        # self.add_output("ERROR", "Failed to send email after multiple attempts.")

    def run(self):
        self.running = True
        schedule.every().day.at(self.scheduled_time.toString('HH:mm')).do(self.job)
        self.log_signal.emit(f"Scheduler started. Waiting for the scheduled time... {self.scheduled_time.toString('HH:mm')}")
        # self.add_output("INFO", f"Scheduler started. Waiting for the scheduled time... {self.scheduled_time.toString('HH:mm')}")
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self.running = False
        self.log_signal.emit("Scheduler stopped. \n =====**************************************************===== \n")
        # self.add_output("INFO", "Scheduler stopped. \n =====**************************************************===== \n")
        
    def job(self):
        try:
            log_info(logger, f"Job started at {datetime.now()}")
            self.log_signal.emit(f"Job started at {datetime.now()}")
            report_data = self.gather_report_data()
            self.send_email(self.email_subject, report_data, self.email_to)
            log_info(logger, f"Job completed at {datetime.now()} \n =====**************************************************===== \n")
            self.log_signal.emit(f"Job completed at {datetime.now()}")
            # self.add_output("SUCCESS", f"Job completed at {datetime.now()}")
        except Exception as e:
            log_error(logger, f"Job failed. Error: {e}")
            self.log_signal.emit(f"Job failed. Error: {e}")
            # self.add_output("ERROR", f"Job failed. Error: {e}")
 
    def add_output(self, output_type, text):
        current_time = datetime.strptime("08/Jan/2012:08:00:00", "%d/%b/%Y:%H:%M:%S").now()
        date_display = f"[{current_time.strftime('%H')}:{current_time.strftime('%M')}:{current_time.strftime('%S')}]"
        output_color = {"ERROR": "red", "WARNING": 'yellow', "INFO": 'gray', "SUCCESS": "green"}

        new_text = f'<div style="color:{output_color[output_type]}; ">{date_display} [{output_type}] {text}</div>'

        scheduler_gui = EmailSchedulerGUI()
        scheduler_gui.log_output.append(new_text)
        
            
class EmailSchedulerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.scheduler_thread = EmailScheduler()
        self.scheduler_thread.log_signal.connect(self.update_log)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Email Scheduler')
        self.setFixedSize(800, 600)  # Fixed window size

        main_layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Email Subject
        self.subject_input = QLineEdit()
        form_layout.addRow("Subject:", self.subject_input)

        # Email Body
        self.body_input = QTextEdit()
        self.body_input.setMinimumHeight(230)
        form_layout.addRow("Body:", self.body_input)

        # Recipient Email and Schedule Time
        email_time_layout = QHBoxLayout()

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Enter recipient email(s), separated by commas")
        email_time_layout.addWidget(self.recipient_input, 80)

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        email_time_layout.addWidget(self.time_input, 20)
        form_layout.addRow("Recipient & Time:", email_time_layout)

        # Start and Stop Buttons
        button_layout = QHBoxLayout()
        start_btn = QPushButton("Start Scheduler")
        start_btn.clicked.connect(self.start_scheduler)
        stop_btn = QPushButton("Stop Scheduler")
        stop_btn.clicked.connect(self.stop_scheduler)
        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)

        # Log Output
        # self.log_output = QTextEdit()
        # self.log_output.setReadOnly(True)
        # self.log_output.setMinimumHeight(100)

        self.log_output = QTextBrowser()
        self.log_output.setStyleSheet(f'padding:0px;')
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_output.setAcceptRichText(True)
        self.log_output.setOpenExternalLinks(True)
        log_label = QLabel("Logs:")

        # Adding widgets to the main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_output, stretch=1)

        self.setLayout(main_layout)

        # Prevent resizing
        self.setFixedSize(self.size())  # Set fixed size based on initial size


    def start_scheduler(self):
        self.scheduler_thread.email_subject = self.subject_input.text()
        self.scheduler_thread.email_body = self.body_input.toPlainText()

        # Split recipient emails from the input line
        recipients = self.recipient_input.text().split(',')
        self.scheduler_thread.email_to = [email.strip() for email in recipients]

        self.scheduler_thread.scheduled_time = self.time_input.time()
        log_info(logger, "Starting scheduler...")  # Informational message
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
