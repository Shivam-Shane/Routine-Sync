import requests
import os
from dotenv import load_dotenv
load_dotenv()

class TursoDatabaseConnect():
    def __init__(self):
        self.database_url= os.getenv("TURSO_DB_URL")  
        self.auth_token = os.getenv("TURSO_DB_AUTH_TOKEN")
        # Check if credentials are set in .env
        if not self.database_url or not self.auth_token:
            raise ValueError("Please set TURSO_DB_URL and TURSO_DB_AUTH_TOKEN in your .env file")
        
        self.headers={
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
            }

    def execute_sql(self,sql,params=None):
        
        if params:
            # Ensure params match the number of placeholders in sql
            placeholders = sql.count("?")
            if placeholders != len(params):
                raise ValueError(f"Number of placeholders ({placeholders}) does not match number of params ({len(params)})")
            # Format params into the SQL string, escaping strings properly
            formatted_params = [f"'{str(p)}'" if isinstance(p, str) else str(p) for p in params]
            sql = sql.replace("?", "{}").format(*formatted_params)
        query={
            "requests": [
                {
                    "type":"execute",
                    "stmt": {
                        "sql": sql, 
                    }
                }
            ]
        }
        
        response = requests.post(f"{self.database_url}/v3/pipeline", json=query, headers=self.headers, timeout=(10, 300))  # 10 sec to connect, 300 sec (5 min) to read response
        response.raise_for_status()
        data = response.json()
        return data
    