# I am building this project to understand how to integrate fastAPI with SQL
import sqlite3
from datetime import datetime
from fastapi import FastAPI, status, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from fastapi.responses import Response, FileResponse
from contextlib import asynccontextmanager

DB_Path = "notes.db"

class NoteCreate(BaseModel):
    title: str
    body: str

class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str

def get_db():
    conn = sqlite3.connect(DB_Path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(DB_Path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        yield
    finally:
        conn.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_index():
    return FileResponse('mini-project-2.html')

@app.get('/notes', response_model=List[Note])
def read_notes(db: sqlite3.Connection = Depends(get_db)):
    notes = db.execute('SELECT * FROM notes').fetchall()
    return [
        {"id": n["id"], "title": n["title"], "body": n["body"], "created_at": n["created_at"]}
        for n in notes
    ]

@app.post('/notes', response_model=Note, status_code=status.HTTP_201_CREATED)
def create_notes(note_in: NoteCreate, db: sqlite3.Connection = Depends(get_db)):
    created_at = datetime.now().isoformat()
    cur = db.execute('''INSERT INTO notes (title, body, created_at) VALUES (?, ?, ?)''', (note_in.title, note_in.body, created_at,))
    db.commit()

    new_id = cur.lastrowid

    return Note(id=new_id,title=note_in.title, body=note_in.body, created_at=created_at)

@app.get('/notes/{id}', response_model=Note)
def read_note(id: int, db: sqlite3.Connection = Depends(get_db)):
    note = db.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return Note(id=id, title=note[1], body=note[2], created_at=note[3])

@app.put('/notes/{id}', response_model=Note, status_code=status.HTTP_200_OK)
def update_note(id: int, note: NoteCreate, db: sqlite3.Connection = Depends(get_db)):
    existing = db.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    if existing is None:
        raise HTTPException(status_code=404, detail="Note not found")
    created_at = existing["created_at"]
    db.execute('''UPDATE notes SET title = ?, body = ?, created_at = ? WHERE id = ?''', (note.title, note.body, created_at, id,))
    db.commit()
    return Note(id=id, title=note.title, body=note.body, created_at=created_at)

@app.delete('/notes/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(id: int, db: sqlite3.Connection = Depends(get_db)):
    existing = db.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    if existing is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.execute('''DELETE FROM notes WHERE id = ?''', (id,))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)