import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, field_validator

DATABASE = Path(os.getenv('TODO_DATABASE', str(Path(__file__).parent / 'todo.db')))


@contextmanager
def database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(app):
    with database() as connection:
        connection.execute(
            'CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)')
    yield


app = FastAPI(title='Simple Todo', lifespan=lifespan)


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator('title')
    @classmethod
    def clean_title(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('Введите текст задачи')
        return value


class TodoUpdate(BaseModel):
    done: bool


class Todo(BaseModel):
    id: int
    title: str
    done: bool


@app.get('/api/todos', response_model=list[Todo])
def list_todos():
    with database() as connection:
        return [dict(row) for row in connection.execute('SELECT * FROM todos ORDER BY id DESC')]


@app.post('/api/todos', response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    with database() as connection:
        cursor = connection.execute('INSERT INTO todos (title) VALUES (?)', (todo.title,))
        return {'id': cursor.lastrowid, 'title': todo.title, 'done': False}


@app.patch('/api/todos/{todo_id}', response_model=Todo)
def update_todo(todo_id: int, todo: TodoUpdate):
    with database() as connection:
        cursor = connection.execute('UPDATE todos SET done = ? WHERE id = ?', (todo.done, todo_id))
        if cursor.rowcount == 0:
            raise HTTPException(404, 'Задача не найдена')
        return dict(connection.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone())


@app.delete('/api/todos/{todo_id}', status_code=204)
def delete_todo(todo_id: int):
    with database() as connection:
        cursor = connection.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(404, 'Задача не найдена')
    return Response(status_code=204)


REVISION_FILE = Path(__file__).resolve().parent.parent / 'revision.txt'
APP_VERSION = (
    REVISION_FILE.read_text().strip()
    if REVISION_FILE.is_file()
    else 'development'
)


@app.get('/api/version')
def version():
<<<<<<< Updated upstream
    return {'version': APP_VERSION}
<<<<<<< Updated upstream
=======
    return {'version': 'manual-002'}

@app.get('/api/health')
def health():
    return {'status': 'ok'}
>>>>>>> Stashed changes
=======

@app.get('/api/health')
def health():
    return {'status': 'ok'}
>>>>>>> Stashed changes
