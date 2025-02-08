from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI()

# Database Connection
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("MYSQL_USER", "myuser")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "mypassword")
DB_NAME = os.getenv("MYSQL_DATABASE", "mydb")

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/users")
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return {"users": users}
