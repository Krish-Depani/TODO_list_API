# Import required modules
import dotenv
import os
import mysql.connector
from fastapi import FastAPI, HTTPException, status
from mysql.connector import errorcode
from pydantic import BaseModel

#loading the environment variables
dotenv.load_dotenv()

# Initialize the todoapi
app = FastAPI()

# Define the To-do task model
class Task(BaseModel):
    task: str
    done: bool

# Connect to the MySQL database
try:
    cnx = mysql.connector.connect(
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        host=os.environ['MYSQL_HOST'],
        database=os.environ['MYSQL_DB'],
    )
    cursor = cnx.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

# Define the authentication middleware
async def authenticate(api_key):
    cursor.execute("SELECT * FROM api_keys WHERE api_key = %s", (api_key,))
    if api_key not in cursor.fetchall()[0]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )

@app.get("/")
async def welcome(api_key: str):
    await authenticate(api_key)
    return "Welcome to To-Do List API"

# Define the GET endpoint to retrieve all tasks
@app.get("/tasks")
async def read_tasks(api_key: str):
    await authenticate(api_key)
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    return tasks

#TODO: include task details in link or somewhere else in post method also done status

# Define the POST endpoint to add a new task
@app.post("/tasks")
async def create_task(task: Task, api_key: str):
    await authenticate(api_key)
    add_task = ("INSERT INTO tasks "
                "(task, done) "
                "VALUES (%s, %s)")
    data_task = (task.task, task.done)
    cursor.execute(add_task, data_task)
    cnx.commit()
    return {"task": task.task}

# Define the PUT endpoint to update a task
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: Task, api_key: str):
    await authenticate(api_key)
    update_task = ("UPDATE tasks "
                   "SET task = %s, done = %s "
                   "WHERE task_id = %s")
    data_task = (task.task, task.done, task_id)
    cursor.execute(update_task, data_task)
    cnx.commit()
    return {"task_id": task_id}

# Define the DELETE endpoint to delete a task
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, api_key: str):
    await authenticate(api_key)
    cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    cnx.commit()
    return {"task_id": task_id}