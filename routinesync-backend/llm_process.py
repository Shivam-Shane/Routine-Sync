import os
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq  # type: ignore
from dotenv import load_dotenv
from templates import template,signature
from pydantic import BaseModel, Field
from logger import logger

load_dotenv()


class MailFormat(BaseModel):
    """
    A model representing a formatted email message with subject and body content.

    This class defines the structure of an email, including a subject line tied to a schedule date
    and an HTML-formatted body constrained to 3 lines of meaningful content. It includes validation
    to ensure proper formatting for use in automated email systems.
    """
    subject: str = Field(
        ...,
        description="The subject of the email, including task name and schedule date  (e.g., 'Task_name Reminder: 2025-03-12').",
        min_length=1,
        max_length=78, 
        example="Kegal_Excercise Reminder: 2025-03-12"
    )
    body: str = Field(
        ...,
        description=(
            "The HTML-formatted body of the email, limited to 5 lines of meaningful content. "
            "For example, a greeting, task details,task importance, and a call-to-action."
        ),
        example="<p>Hello,</p><p>Your task 'Meeting Prep' is due on 2025-03-12.</p><p>Please review it soon!</p>"
    )


class MessageBodyCreation:
    """
    A class to generate email message bodies using the ChatGroq model.

    """
    def __init__(self):
        """
        Initialize chat model
        """
        try:
            self.chat_model = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.4
            )
            logger.info("ChatGroq model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChatGroq model: {e}")
            raise

    def create_body(self, task: str, task_desc: str, schedule_time: str) -> dict | None:
        """
        Generates an email message body based on input task details.

        Args:
            task (str): The main task name.
            task_desc (str): Description of the task.
            schedule_time (str): Scheduled date/time.

        Returns:
            dict | None: Generated email subject and body if successful, else None.
        """
        try:
            logger.info(f"Generating email body for task: {task}, schedule: {schedule_time}")

            # Structured output model
            model_with_structured_reply = self.chat_model.with_structured_output(MailFormat)
            prompt_template = PromptTemplate.from_template(template)

            # Pipeline chain execution
            chain = prompt_template | model_with_structured_reply
            result = chain.invoke({
                'Task': task,
                'Task_Description': task_desc,
                'Schedule_Date': schedule_time
            })

            result.body=result.body+signature

            logger.info("Email body successfully generated")
            return result

        except Exception as e:
            logger.error(f"Error in creating mail body: {e}")
            return None

