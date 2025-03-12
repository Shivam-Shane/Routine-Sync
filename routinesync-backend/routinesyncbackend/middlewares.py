# routinesync-backend/middleware.py
from django.http import JsonResponse #type: ignore
import os, sys

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)

from dotenv import load_dotenv
from logger import logger
load_dotenv()
class APIKeyMiddleware:
    """Middleware to validate API key and UI access key"""

    def __init__(self, get_response):
        self.get_response = get_response
        #ips list of cronjob.org
        self.allowed_ips = [
            "116.203.134.67",
            "116.203.129.16",
            "23.88.105.37",
            "128.140.8.200"
        ]
        self.allowed_paths = ["/api/reminder/", "/api/validate-ui-key/"]  # Exempt these paths

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        # In settings.py or middleware
        required_vars = ["API_KEY", "UI_ACCESS_KEY"]
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"Missing required environment variable: {var}")
                raise ValueError(f"Missing required environment variable: {var}")
            
        # Skip validation for allowed paths or IPs
        if request.path not in self.allowed_paths and ip not in self.allowed_ips:
            
            api_key = request.headers.get("X-API-KEY")
            valid_api_key = os.getenv("API_KEY")
            if not valid_api_key:
                logger.warning(f"valid_api_key not found in env")
                return JsonResponse({"error": "Server configuration error"}, status=500)
            if not api_key or api_key != valid_api_key:
                logger.warning(f"Invalid Api key hit from {ip}")
                return JsonResponse({"error": "Unauthorized: Invalid API Key"}, status=401)

            ui_access_key = request.headers.get("X-UI-ACCESS-KEY")
            valid_ui_key = os.getenv("UI_ACCESS_KEY")
            if not ui_access_key or ui_access_key != valid_ui_key:
                return JsonResponse({"error": "Forbidden: Invalid UI Access Key"}, status=403)

        
        response = self.get_response(request)
        return response