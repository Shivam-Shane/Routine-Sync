# RoutineSync

RoutineSync is a task management web application built with React that allows users to create, view, and manage scheduled tasks with recurrence options. The app integrates with a Turso database for persistence, uses Grafana Cloud with Loki for logging, and leverages cron-job.org for email reminders.

## Features

- Create tasks with name, description, schedule time, and recurrence options
- View active and archived tasks
- Delete tasks
- UI Access Key authentication
- Responsive design with loading states
- Recurrence options: Once, Daily, Alternate Days, Weekly, Monthly
- Real-time validation for future scheduling
- Email reminders for tasks with dynamically generated email body and subject using a chat model(LLM)

## Tech Stack

- **Frontend**: React
- **Database**: Turso (SQLite-based)
- **Logging**: Grafana Cloud with Loki
- **Task Scheduling**: cron-job.org (open-source)
- **Icons**: Font Awesome (free version)

## Prerequisites

- Node.js (v22.13.0 or later recommended)
- npm (v10.9.2 or later)
- Turso database account and credentials
- Grafana Cloud account for logging
- cron-job.org account for task scheduling
- Backend API service configured with above services

# Logging

## Grafana Cloud with Loki
- Stores application logs
- Provides monitoring and debugging capabilities
- Integrated with backend API

# Task Scheduling

## cron-job.org
- Open-source scheduling service
- Invokes reminder API for email notifications
- Configured to match task recurrence patterns

# API Endpoints Used
- **POST /api/validate-ui-key/** - Validate UI Access Key
- **GET /api/tasks/** - Fetch active tasks from Turso
- **GET /api/tasks/archived/** - Fetch archived tasks from Turso
- **POST /api/tasks/create/** - Create new task in Turso
- **POST /api/tasks/delete/** - Delete task from Turso

# Authentication
- **X-API-KEY**: Backend API authentication (stored in `.env`)
- **X-UI-Access-Key**: UI-level access control (user-provided, stored in `localStorage`)

# Email Reminders
- Configured through cron-job.org
- Triggers email notifications based on task schedule
- Email body and subject dynamically generated using a chat model
- Integrates with reminder API endpoint
- Supports all recurrence patterns

# Development Notes
- Error handling implemented with try/catch blocks
- Loading states managed for all async operations
- Tasks normalized before adding to state
- Minimum schedule time set to current date/time
- ESLint configured (exhaustive-deps warning disabled)
- Logs sent to Grafana Cloud for monitoring

# Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

# Monitoring
- Access Grafana Cloud dashboard for logs
- Monitor API performance and errors via Loki
- Track cron-job.org execution status

## License
This project is licensed under the Creative Commons Zero v1.0 Universal - see the LICENSE file for details.

## Contact

For questions, suggestions, or support, reach out at 
- **sk0551460@gmail.com** 
- **shivam.hireme@gmail.com**.

## Support the Project

Help support continued development and improvements:

- **Follow on LinkedIn**: Stay connected for updates – [LinkedIn Profile](https://www.linkedin.com/in/shivam-hireme/)
- **Buy Me a Coffee**: Appreciate the project? [Buy Me a Coffee](https://buymeacoffee.com/shivamshane)
- **Visit my Portfolio**: [Shivam's Portfolio](https://shivam-portfoliio.vercel.app/)
