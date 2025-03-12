PRAGMA foreign_keys = ON;

CREATE TABLE routinesynctaskdata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Task TEXT,
    Task_Description TEXT,
    Schedule_Date TEXT,
    recurrence TEXT
)

CREATE TABLE routinesynctask_sentdetails (
    id INTEGER,
    Task TEXT,
    "Last_Sent" TEXT DEFAULT '0001-01-01T00:01',
    FOREIGN KEY (id) REFERENCES routinesynctaskdata(id) ON DELETE CASCADE
)

CREATE TABLE archived_tasks (
    id INTEGER,
    Task TEXT,
    Schedule_Date TEXT,
    Last_Sent TEXT
)


DROP TRIGGER IF EXISTS "main"."Insert_into_sent_details_when_any_insert_is_happen";
CREATE TRIGGER "Insert_into_sent_details_when_any_insert_is_happen" 
AFTER INSERT ON "routinesynctaskdata" 
FOR EACH ROW 
BEGIN 
	INSERT INTO routinesynctask_sentdetails (id, Task)
    VALUES (NEW.id, NEW.Task); 
END


DROP TRIGGER IF EXISTS "main"."archive_task_trigger";
CREATE TRIGGER "archive_task_trigger" 
BEFORE DELETE ON "routinesynctaskdata" 
FOR EACH ROW 
BEGIN 
	INSERT INTO archived_tasks (id, Task, Schedule_Date, Last_Sent)
    VALUES (
        OLD.id, 
        OLD.Task, 
        OLD.Schedule_Date, 
        (SELECT Last_Sent FROM routinesynctask_sentdetails WHERE id = OLD.id LIMIT 1)
    ); 
END

