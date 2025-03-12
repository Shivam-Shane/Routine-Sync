import React, { useState, useEffect } from 'react';
import '../styles/home.css';
import Footer from './Footer';
import '@fortawesome/fontawesome-free/css/all.min.css';

const Home = () => {
  const [tasks, setTasks] = useState([]);
  const [archivedTasks, setArchivedTasks] = useState([]);
  const [taskName, setTaskName] = useState('');
  const [taskDesc, setTaskDesc] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  const [recurrence, setRecurrence] = useState('once');
  const [showArchived, setShowArchived] = useState(false);
  const [minDateTime, setMinDateTime] = useState(new Date().toISOString().slice(0, 16));
  const [uiAccessKey, setUiAccessKey] = useState(localStorage.getItem('X-UI-Access-Key') || '');
  const [showKeyPrompt, setShowKeyPrompt] = useState(!localStorage.getItem('X-UI-Access-Key'));
  const [tempKey, setTempKey] = useState('');
  const [loadingTasks, setLoadingTasks] = useState(false); // Loading state for fetching tasks
  const [loadingArchivedTasks, setLoadingArchivedTasks] = useState(false); // Loading state for archived tasks
  const [loadingAddTask, setLoadingAddTask] = useState(false); // Loading state for adding tasks
  const [loadingDeleteTask, setLoadingDeleteTask] = useState(null); // Loading state for deleting tasks (taskId)
  const [loadingKeyValidation, setLoadingKeyValidation] = useState(false); // Loading state for key validation
  const API_KEY = process.env.REACT_APP_API_KEY;

  useEffect(() => {
    if (uiAccessKey) {
      fetchTasks();
      fetchArchivedTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uiAccessKey]);

  const validateKey = async (key) => {
    setLoadingKeyValidation(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/validate-ui-key/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': API_KEY,
          'X-UI-Access-Key': key,
        },
      });

      if (!response.ok) throw new Error('Invalid UI Access Key');

      return true;
    } catch (error) {
      console.error(error.message);
      return false;
    } finally {
      setLoadingKeyValidation(false);
    }
  };

  const handleKeySubmit = async (e) => {
    e.preventDefault();
    const isValid = await validateKey(tempKey);
    if (isValid) {
      setUiAccessKey(tempKey);
      localStorage.setItem('X-UI-Access-Key', tempKey);
      setShowKeyPrompt(false);
    } else {
      alert('Invalid UI Access Key');
    }
  };

  const handleNoKey = () => {
    setShowKeyPrompt(false);
  };

  const fetchTasks = async () => {
    setLoadingTasks(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/tasks/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': API_KEY,
          'X-UI-Access-Key': uiAccessKey,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch tasks');
      const data = await response.json();
      setTasks(data);
    } catch (error) {
    } finally {
      setLoadingTasks(false);
    }
  };

  const fetchArchivedTasks = async () => {
    setLoadingArchivedTasks(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/tasks/archived/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': API_KEY,
          'X-UI-Access-Key': uiAccessKey,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch archived tasks');
      const data = await response.json();
      setArchivedTasks(data);
    } catch (error) {
    } finally {
      setLoadingArchivedTasks(false);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    const now = new Date();
    const selectedTime = new Date(scheduleTime);
    if (selectedTime <= now) {
      alert('Please select a future date and time.');
      return;
    }
    if (taskName && scheduleTime) {
      const newTask = {
        Task: taskName,
        Task_Description: taskDesc,
        Schedule_Date: scheduleTime,
        recurrence: recurrence,
        completed: '0',
      };
      setLoadingAddTask(true);
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/tasks/create/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': API_KEY,
            'X-UI-Access-Key': uiAccessKey,
          },
          body: JSON.stringify(newTask),
        });
        if (!response.ok) throw new Error('Failed to create task');
        const createdTaskList = await response.json();
        const createdTask = createdTaskList[createdTaskList.length - 1];
        const normalizedTask = {
          id: createdTask.id || createdTask.task_id,
          Task: createdTask.Task || createdTask.task,
          Task_Description: createdTask.Task_Description || createdTask.description,
          Schedule_Date: createdTask.Schedule_Date || createdTask.schedule_date,
          recurrence: createdTask.recurrence,
          completed: createdTask.completed,
        };
        setTasks([...tasks, normalizedTask]);
        setTaskName('');
        setTaskDesc('');
        setScheduleTime('');
        setRecurrence('once');
      } catch (error) {
      } finally {
        setLoadingAddTask(false);
      }
    }
  };

  const handleDeleteTask = async (taskId) => {
    setLoadingDeleteTask(taskId);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/tasks/delete/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': API_KEY,
          'X-UI-Access-Key': uiAccessKey,
        },
        body: JSON.stringify({ task_id: taskId }),
      });
      if (!response.ok) throw new Error('Failed to delete task');
      setTasks(tasks.filter((task) => task.id !== taskId));
    } catch (error) {
    } finally {
      setLoadingDeleteTask(null);
    }
  };

  return (
    <div className="home-container">
      {showKeyPrompt && (
        <div className="key-prompt-overlay">
          <div className="key-prompt">
            <h2>Enter UI Access Key</h2>
            <form onSubmit={handleKeySubmit}>
              <input
                type="text"
                value={tempKey}
                onChange={(e) => setTempKey(e.target.value)}
                placeholder="Enter your UI Access Key"
                required
                disabled={loadingKeyValidation}
              />
              <button type="submit" disabled={loadingKeyValidation}>
                {loadingKeyValidation ? 'Validating...' : 'Submit'}
              </button>
              <button type="button" onClick={handleNoKey} disabled={loadingKeyValidation}>
                I Don’t Have a Key
              </button>
            </form>
          </div>
        </div>
      )}

      <div className="header-container">
        <h1>RoutineSync</h1>
        {uiAccessKey && (
          <button
            className="archive-toggle-button"
            onClick={() => setShowArchived(!showArchived)}
          >
            {showArchived ? 'Show Active Tasks' : 'Archive Tasks'}
          </button>
        )}
      </div>

      {!showArchived ? (
        <>
          <div className="task-list">
            <h2>Your Tasks</h2>
            {!uiAccessKey ? (
              <p>Enter a UI Access Key to view and manage tasks.</p>
            ) : loadingTasks ? (
              <p>Loading tasks...</p>
            ) : tasks.length === 0 ? (
              <p>No tasks yet. Add some tasks above!</p>
            ) : (
              <ul>
                {tasks.map((task) => (
                  <li key={task.id} className="task-item">
                    <div>
                      <h3>{task.Task}</h3>
                      <p>{task.Task_Description}</p>
                      <small>
                        Scheduled: {new Date(task.Schedule_Date).toLocaleString()}
                        {task.recurrence !== 'once' && ` (${task.recurrence})`}
                      </small>
                    </div>
                    <div>
                      <button
                        className="delete-button"
                        onClick={() => handleDeleteTask(task.id)}
                        disabled={loadingDeleteTask === task.id}
                      >
                        {loadingDeleteTask === task.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {uiAccessKey && (
            <form onSubmit={handleAddTask} className="task-form">
              <div className="form-group">
                <label htmlFor="taskName">Task Name</label>
                <input
                  type="text"
                  id="taskName"
                  value={taskName}
                  onChange={(e) => setTaskName(e.target.value)}
                  placeholder="Enter task name"
                  required
                  disabled={loadingAddTask}
                />
              </div>
              <div className="form-group">
                <label htmlFor="taskDesc">Description</label>
                <textarea
                  id="taskDesc"
                  value={taskDesc}
                  onChange={(e) => setTaskDesc(e.target.value)}
                  placeholder="Enter task description"
                  rows="3"
                  disabled={loadingAddTask}
                />
              </div>
              <div className="form-group">
                <label htmlFor="scheduleTime">Schedule Time</label>
                <input
                  type="datetime-local"
                  id="scheduleTime"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  onFocus={() => setMinDateTime(new Date().toISOString().slice(0, 16))}
                  min={minDateTime}
                  required
                  disabled={loadingAddTask}
                />
              </div>
              <div className="form-group">
                <label htmlFor="recurrence">Recurrence</label>
                <select
                  id="recurrence"
                  value={recurrence}
                  onChange={(e) => setRecurrence(e.target.value)}
                  className="recurrence-select"
                  disabled={loadingAddTask}
                >
                  <option value="once">Once</option>
                  <option value="daily">Daily</option>
                  <option value="alternate">Alternate Days</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <button type="submit" className="add-button" disabled={loadingAddTask}>
                {loadingAddTask ? 'Adding Task...' : 'Add Task'}
              </button>
            </form>
          )}
        </>
      ) : (
        <div className="task-list">
          <h2>Archived Tasks</h2>
          {!uiAccessKey ? (
            <p>Enter a UI Access Key to view archived tasks.</p>
          ) : loadingArchivedTasks ? (
            <p>Loading archived tasks...</p>
          ) : archivedTasks.length === 0 ? (
            <div className="no-tasks-container">
              <i className="fas fa-archive no-tasks-icon"></i>
              <p className="no-tasks-message">No archived tasks yet</p>
            </div>
          ) : (
            <ul>
              {archivedTasks.map((task) => (
                <li key={task.id} className="task-item archived">
                  <div>
                    <h3>{task.Task}</h3>
                    <p>{task.Task_Description}</p>
                    <small>
                      Scheduled: {new Date(task.Schedule_Date).toLocaleString()}
                      
                    </small>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      <Footer />
    </div>
  );
};

export default Home;