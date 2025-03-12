# templates.py

template = """
You are a helpful AI email writer. Please compose a clear and concise reminder email based on the details below:  

**Task:** {Task}  
**Task Description:** {Task_Description}  
**Scheduled Date:** {Schedule_Date}  

This email should serve as a friendly reminder to ensure the recipient completes their task on time. Keep it professional, structured, and to the point.  
Don't Include Any Greeting and signatures in this email
"""

signature = """
<div style="margin-top: 20px; font-family: Arial, sans-serif; font-size: 12px; color: #555;">
    <p>Best regards,</p>
    <p><strong>RoutineSync Team</strong></p>
    <p><a href="https://routinesync.vercel.app/" style="color: #007BFF; text-decoration: none;">https://routinesync.vercel.app/</a></p>
</div>
"""