from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.get("/api/parameters")
def read_parameters():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, value, updated_at FROM parameters;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"name": r[0], "value": r[1], "updated_at": r[2]} for r in rows]
