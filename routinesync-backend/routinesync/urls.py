
# routinesync/urls.py
from django.urls import path#type: ignore
from routinesyncbackend.views import (task_list, task_create,
            delete_task,archive_task,reminder,validate_ui_key)  # Import views from your app

urlpatterns = [
    path('api/tasks/', task_list, name='task_list'),
    path('api/tasks/create/', task_create, name='task_create'),
    path('api/tasks/delete/', delete_task, name='delete_task'),
    path('api/tasks/archived/', archive_task, name='archive_task'),
    path('api/reminder/', reminder, name='reminder'),  # Added trailing slash
    path('api/validate-ui-key/', validate_ui_key, name="validate_ui_key")  # Added trailing slash
]