# RoutineSync Backend  

RoutineSync's backend handles task storage, authentication, logging, and scheduling integrations. It integrates with a Turso database for persistence, uses Grafana Cloud with Loki for logging, and leverages cron-job.org for email reminders.  

## Features  

- Store and retrieve scheduled tasks  
- Validate UI Access Keys  
- Log application activities for monitoring  
- Schedule task reminders via cron-job.org  
- Secure API authentication using X-API-KEY  

## Tech Stack  

- **Database**: Turso (SQLite-based)  
- **Logging**: Grafana Cloud with Loki  
- **Task Scheduling**: cron-job.org (open-source)  

## Logging  

### Grafana Cloud with Loki  

- Stores application logs  
- Provides monitoring and debugging capabilities  
- Integrated with backend API  

## Task Scheduling  

### cron-job.org  

- Open-source scheduling service  
- Invokes reminder API for email notifications  
- Configured to match task recurrence patterns  

## API Endpoints  

- **POST /api/validate-ui-key/** - Validate UI Access Key  
- **GET /api/tasks/** - Fetch active tasks from Turso  
- **GET /api/tasks/archived/** - Fetch archived tasks from Turso  
- **POST /api/tasks/create/** - Create new task in Turso  
- **POST /api/tasks/delete/** - Delete task from Turso  

## Authentication  

- **X-API-KEY**: Backend API authentication (stored in `.env`)  
- **X-UI-Access-Key**: UI-level access control (user-provided, stored in `localStorage`)  

## Email Reminders  

- Configured through cron-job.org  
- Triggers email notifications based on task schedule  
- Integrates with reminder API endpoint  
- Supports all recurrence patterns  

## Monitoring  

- Access Grafana Cloud dashboard for logs  
- Monitor API performance and errors via Loki  
- Track cron-job.org execution status  

## License  

This project is licensed under the GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.  

## Contact  

For any questions or support, please contact the project maintainer at sk0551460@gmail.com  
