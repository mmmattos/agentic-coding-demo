from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List
import uvicorn

app = FastAPI()

DATABASE = "notes.db"

class NoteIn(BaseModel):
    content: str

class NoteOut(BaseModel):
    id: int
    content: str

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/notes", response_model=NoteOut)
def create_note(note: NoteIn):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (content) VALUES (?)", (note.content,))
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return { "id": note_id, "content": note.content }

@app.get("/notes", response_model=List[NoteOut])
def read_notes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM notes")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row["id"], "content": row["content"]} for row in rows]

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)