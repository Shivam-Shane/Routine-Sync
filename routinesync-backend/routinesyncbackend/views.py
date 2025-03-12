# routinesync-backend/views.py
import os, sys
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
import requests
from rest_framework.decorators import api_view #type: ignore
from rest_framework.response import Response #type: ignore
from django.http import JsonResponse #type: ignore
from rest_framework import status #type: ignore
from dotenv import load_dotenv
from turso_connect import TursoDatabaseConnect
from task_reminder import ReminderSystem
from logger import logger
# Load environment variables
load_dotenv()
# Instantiate Turso client
client = TursoDatabaseConnect()
reminder_system = ReminderSystem()
@api_view(['POST'])
def validate_ui_key(request):
    """
    Validate the X-UI-ACCESS-KEY sent from the frontend.
    """
    ui_access_key = request.headers.get("X-UI-ACCESS-KEY")  # Consistent naming
    valid_ui_key = os.getenv("UI_ACCESS_KEY")
    
    logger.info(f"Received UI Key: {ui_access_key}, Type: {type(ui_access_key)}, Length: {len(ui_access_key) if ui_access_key else 0}")
    
    if not ui_access_key or ui_access_key != valid_ui_key:
        logger.info("Validation failed: Keys don't match or missing")
        return Response({"error": "Invalid UI Access Key"}, status=status.HTTP_403_FORBIDDEN)
    
    logger.info("Validation succeeded")
    return Response({"message": "UI Access Key validated"}, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------------------------------------
@api_view(['GET'])
def task_list(request):
    """
    List all tasks from the Turso database.
    """
    try:
        result = client.execute_sql("SELECT * FROM routinesynctaskdata")

        if not result["results"]:
            logger.error("No response received from the database.")
            return Response({"error": "Unable to retrieve tasks at the moment. Please try again later."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        first_result = result["results"][0]

        if first_result["type"] == "ok":
            tasks = result_parser_tojson(result)
            return Response(tasks, status=status.HTTP_200_OK)

        if first_result["type"] == "error":
            error_message = first_result["error"].get("message", "Unknown database error")
            logger.error(f"Database Error: {error_message}")
            return Response({"error": f"Task retrieval failed: {error_message}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except requests.RequestException as e:
        logger.error(f"Request Exception: {str(e)}")
        return Response({"error": "Network issue encountered. Please check your connection and try again."}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return Response({"error": "An unexpected error occurred. Please try again later."}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#--------------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def task_create(request):
    """
    Create a new task in the Turso database.
    """
    data = request.data
    required_fields = ["Task", "Schedule_Date"]

    # Validate required fields
    if not all(field in data for field in required_fields):
        logger.warning("Task creation failed: Missing required fields.")
        return Response(
            {"error": "Missing required fields: Task and Schedule_Date are required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        params = (
            data.get("Task"),
            data.get("Task_Description", ""),  # Default to empty if not provided
            data.get("Schedule_Date"),
            data.get("recurrence", "once")  # Default recurrence to 'once'
        )

        # Insert task into database
        result = client.execute_sql(
            sql="INSERT INTO routinesynctaskdata (Task, Task_Description, Schedule_Date, recurrence) VALUES (?, ?, ?, ?)",
            params=params
        )

        # Check for database errors
        if not result["results"]:
            logger.error("Database error: No response received from the database.")
            return Response(
                {"error": "Task creation failed due to a server issue. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        first_result = result["results"][0]

        if first_result["type"] == "error":
            error_message = first_result["error"].get("message", "Unknown database error")
            logger.error(f"Database Error: {error_message}")
            return Response(
                {"error": f"Task creation failed: {error_message}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Check if a row was successfully inserted
        if first_result.get("response", {}).get("result", {}).get("affected_row_count", 0) == 1:
            new_task_result = client.execute_sql("SELECT * FROM routinesynctaskdata ORDER BY id DESC LIMIT 1")
            new_task = result_parser_tojson(new_task_result)

            logger.info(f"Successfully created Task: {new_task}")
            return Response(new_task, status=status.HTTP_201_CREATED)

        logger.warning("Task creation failed: No rows affected.")
        return Response(
            {"error": "Task creation unsuccessful. Please check the provided data."},
            status=status.HTTP_400_BAD_REQUEST
        )

    except requests.RequestException as e:
        logger.error(f"Request Exception: {str(e)}")
        return Response(
            {"error": "Network issue encountered. Please check your connection and try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

#--------------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def delete_task(request):
    """
    Delete task in the Turso database.
    """
    data_deletion = request.data

    try:
        query = "DELETE FROM routinesynctaskdata WHERE id = ?"
        params = ([data_deletion.get("task_id")])
        result = client.execute_sql(query, params)

        if result["results"][0]["response"]["result"]["affected_row_count"] == 1:
            logger.info("Record deleted successfully")
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)
        elif result["results"][0]["response"]["result"]["affected_row_count"] == 0:
            logger.warning("No record available to delete")
            return Response({"message": "No task present"}, status=status.HTTP_404_NOT_FOUND)
        if result['results'][0]["type"] == 'error':
            logger.error(f"Error occured while deleting record {result['results'][0]['error']['message']}")
            return Response({"error": "Failed to delete task"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.RequestException as e:
        logger.error(f"Error occured while deleting record {e}")
        return Response({"error": f"Failed to delete task: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return Response({"error": "Unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#--------------------------------------------------------------------------------------------------------------------------
@api_view(['GET', 'POST'])
def archive_task(request):
    """
    GET: List all archived tasks.
    POST: Archive a task by moving it to archived_tasks.
    """
    if request.method == 'GET':
        try:
            result = client.execute_sql("SELECT * FROM archived_tasks")
            if result['results'][0]["type"] == 'ok':
                tasks = result_parser_tojson(result)
                return Response(tasks, status=status.HTTP_200_OK)
            if result['results'][0]["type"] == 'error':
                return Response({"error": f"Failed to fetch archive tasks: {result['results'][0]['error']['message']}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            return Response({"error": f"Failed to fetch archived tasks: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'POST':
        task_id = request.data.get("task_id")
        if not task_id:
            return Response({"error": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Move task to archived_tasks
            result = client.execute_sql(
                sql="INSERT INTO archived_tasks SELECT * FROM routinesynctaskdata WHERE id = ?",
                params=(task_id,)
            )
            if result['results'][0]["type"] == 'error':
                return Response({"error": f"Failed to archive task: {result['results'][0]['error']['message']}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if result["results"][0]["response"]["result"]["affected_row_count"] == 1:
                # Delete from original table
                client.execute_sql("DELETE FROM routinesynctaskdata WHERE id = ?", (task_id,))
                return Response({"message": "Task archived successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "Task archiving failed"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({"error": f"Failed to archive task: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#--------------------------------------------------------------------------------------------------------------------------
@api_view(['POST'])
def reminder(request):
    try:
        reminder_api_key = request.data.get("REMINDER_API_KEY") or None
        if not reminder_api_key:
            logger.warning("Missing REMINDER_API_KEY in request.")
            return Response({"error": "Missing reminderapi_key"}, status=status.HTTP_400_BAD_REQUEST)
        if reminder_api_key!=os.getenv("REMINDER_API_KEY"):
            logger.warning("Incorrect REMINDER_API_KEY in request.")
            return Response({"error": "Incorrect REMINDER_API_KEY"}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"Received REMINDER_API_KEY: {reminder_api_key}")

        query = """
            SELECT routinesynctaskdata.*, Last_Sent
            FROM routinesynctaskdata 
            JOIN routinesynctask_sentdetails
            ON routinesynctaskdata.id = routinesynctask_sentdetails.id
        """

        try:
            query_result = client.execute_sql(query)
            logger.info(f"Query executed successfully. Response: {query_result}")
        except Exception as sql_error:
            logger.error(f"SQL execution failed: {sql_error}")
            return Response({"error": "Database query failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Validate tasks response structure
        try:
            task_results = query_result.get("results", [])
            if not task_results or "response" not in task_results[0] or "result" not in task_results[0]["response"]:
                logger.error("Unexpected database response structure.")
                return Response({"error": "Unexpected database response format"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            rows = task_results[0]["response"]["result"].get("rows", [])
        except (IndexError, KeyError, TypeError) as parse_error:
            logger.error(f"Error parsing database response: {parse_error}")
            return Response({"error": "Error processing database response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not rows:
            logger.info("No data found to process.")
            return Response({"message": "No Data to run task present"}, status=status.HTTP_200_OK)

        # Process result
        try:
            database_query_structured_result = result_parser_tojson(query_result)
            logger.info(f"Parsed query result: {database_query_structured_result}")
        except Exception as parse_error:
            logger.error(f"Error parsing query result: {parse_error}")
            return Response({"error": "Failed to process task results"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Execute main task function
        try:
            if reminder_system.main(database_query_structured_result):
                logger.info("Task processed successfully.")
                return Response({"message": "Finished Processing Task"}, status=status.HTTP_200_OK)
        except Exception as task_error:
            logger.error(f"Task processing failed: {task_error}")
            return Response({"error": "Task processing failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info("No pending tasks for processing.")
        return Response({"message": "No Task Pending for Processing"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Unexpected error occurred in the reminder function.")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#--------------------------------------------------------------------------------------------------------------------------
def result_parser_tojson(result):
    """
    Parses a database result into a JSON-compatible list of dictionaries.

    Args:
        result (dict): The database query result containing 'results', 'response', 'result', 'cols', and 'rows'.

    Returns:
        list: A list of dictionaries representing the parsed database rows.
    """
    try:
        # Validate result structure before accessing keys
        if not isinstance(result, dict) or "results" not in result or not result["results"]:
            logger.error("Invalid result format: Missing 'results' key or empty list")
            raise ValueError("Invalid result format: Missing 'results' key or empty list")

        response = result["results"][0].get("response", {})
        db_result = response.get("result", {})

        if "cols" not in db_result or "rows" not in db_result:
            logger.error("Invalid result format: Missing 'cols' or 'rows' in response")
            raise ValueError("Invalid result format: Missing 'cols' or 'rows' in response")

        # Extract column names
        columns = [col["name"] for col in db_result["cols"]]

        # Extract row values
        rows = [[cell.get("value") for cell in row] for row in db_result["rows"]]

        # Convert rows to JSON format
        tasks = [dict(zip(columns, row)) for row in rows]

        logger.info(f"{len(tasks)} records successfully parsed to JSON format")
        return tasks

    except KeyError as e:
        logger.error(f"KeyError in result parsing: Missing key {e}")
    except ValueError as e:
        logger.error(f"ValueError in result parsing: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in result parsing: {e}")

    return None  # Return None if parsing fails
