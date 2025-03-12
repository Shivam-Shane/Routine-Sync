import os
from typing import List, Dict
import pendulum  # type: ignore
from turso_connect import TursoDatabaseConnect
from gmail_connector import MailSender
from llm_process import MessageBodyCreation
from logger import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")  # Default to Asia/Kolkata if not set

# Instantiate clients
class ReminderSystem:
    def __init__(self):
        self.mail_sender = MailSender()
        self.email_body_creator = MessageBodyCreation()
        self.db_client = TursoDatabaseConnect()
        self.current_dt = pendulum.now(TIMEZONE)
        self.lower_bound = self.current_dt.subtract(minutes=20)
        self.upper_bound = self.current_dt.add(minutes=25)

    def update_last_sent(self, schedule_date: str, task_id: str) -> bool:
        """Update the Last_Sent timestamp for a task in the database."""
        query = """UPDATE routinesynctask_sentdetails SET Last_Sent = (?) WHERE id = (?)"""
        params = (schedule_date, task_id)
        
        try:
            result = self.db_client.execute_sql(query, params)
            if not result.get("results"):
                logger.error("No response received from the database.")
                return False
            affected_rows = result["results"][0]["response"]["result"]["affected_row_count"]
            if affected_rows >= 1:
                logger.info(f"Last Sent updated successfully for task {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating Last_Sent for task {task_id}: {str(e)}")
            return False

    def send_reminder(self, task: Dict) -> bool:
        """Send email reminder and return success status."""
        result = self.email_body_creator.create_body(
            task["Task"], task["Task_Description"], task["Schedule_Date"]
        )
        return self.mail_sender.sender(
            "sk0551460@gmail.com", result.subject, result.body
        )

    def process_task(self, task: Dict) -> None:
        """Process a single task based on its recurrence type."""
        schedule_dt = pendulum.parse(task["Schedule_Date"], tz=TIMEZONE)
        last_sent = pendulum.parse(task["Last_Sent"], tz=TIMEZONE)
        within_time_range = self.lower_bound.time() <= schedule_dt.time() <= self.upper_bound.time()
        
        recurrence_handlers = {
            "daily": self._handle_daily,
            "once": self._handle_once,
            "weekly": self._handle_weekly,
            "monthly": self._handle_monthly,
        }

        handler = recurrence_handlers.get(task["recurrence"])
        if handler:
            handler(task, schedule_dt, last_sent, within_time_range)
        else:
            logger.warning(f"Unknown recurrence type: {task['recurrence']} for task {task['Task']}")

    def _handle_daily(self, task: Dict, schedule_dt: pendulum.DateTime, 
                     last_sent: pendulum.DateTime, within_time_range: bool) -> None:
        logger.info("Processing daily task...")
        logger.info(f"Scedule {schedule_dt} --- {last_sent} --- {within_time_range}")
        logger.info(f"Upper range {self.upper_bound}  lower range {self.lower_bound}")
        if within_time_range and last_sent.date() != self.current_dt.date():
            if self.send_reminder(task):
                logger.info(f"Reminder sent for daily task: {task['Task']}")
                self.update_last_sent(task["Schedule_Date"], task["id"])
        else:
            logger.info(f"Daily task {task['Task']} not in range or already sent today.")

    def _handle_once(self, task: Dict, schedule_dt: pendulum.DateTime, 
                    last_sent: pendulum.DateTime, within_time_range: bool) -> None:
        logger.info("Processing one-time task...")
        if within_time_range:
            if self.send_reminder(task):
                logger.info(f"Reminder sent for one-time task: {task['Task']}")
                if self.update_last_sent(task["Schedule_Date"], task["id"]):
                    query = """DELETE FROM routinesynctaskdata WHERE id = (?)"""
                    if self.db_client.execute_sql(query, (task["id"],)):
                        logger.info(f"Task {task['Task']} completed and archived.")
        else:
            logger.info(f"One-time task {task['Task']} not in range.")

    def _handle_weekly(self, task: Dict, schedule_dt: pendulum.DateTime, 
                      last_sent: pendulum.DateTime, within_time_range: bool) -> None:
        logger.info("Processing weekly task...")
        next_weekly = last_sent.add(days=7).date()
        if (schedule_dt.date() == self.current_dt.date() or 
            (next_weekly == self.current_dt.date() and last_sent.date() != self.current_dt.date())):
            if within_time_range and self.send_reminder(task):
                logger.info(f"Reminder sent for weekly task: {task['Task']}")
                self.update_last_sent(task["Schedule_Date"], task["id"])
        else:
            logger.info(f"Weekly task {task['Task']} not due today.")

    def _handle_monthly(self, task: Dict, schedule_dt: pendulum.DateTime, 
                       last_sent: pendulum.DateTime, within_time_range: bool) -> None:
        logger.info("Processing monthly task...")
        next_monthly = last_sent.add(months=1).date()
        if (schedule_dt.date() == self.current_dt.date() or 
            (next_monthly == self.current_dt.date() and last_sent.date() != self.current_dt.date())):
            if within_time_range and self.send_reminder(task):
                logger.info(f"Reminder sent for monthly task: {task['Task']}")
                self.update_last_sent(task["Schedule_Date"], task["id"])
        else:
            logger.info(f"Monthly task {task['Task']} not due today.")

    def main(self, tasks: List[Dict]) -> int:
        """Main function to process all tasks."""
        logger.info("Running Main Reminder Task")
        for task in tasks:
            self.process_task(task)
        return 1
