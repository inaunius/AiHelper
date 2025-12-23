# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import os
from datetime import datetime
from analyzer import _make_report

app = FastAPI(
    title="AI-помощник: Мониторинг изменений законодательства",
    description="Прототип для ООО «Газпромнефть-ЦР»",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LawChange(BaseModel):
    id: int
    title: str
    url: str
    date: str
    description: str

@app.get("/api/changes", response_model=List[LawChange])
def get_changes():
    db_path = "laws.db"
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="База данных laws.db не найдена. Запустите: python main.py")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, url, date, description FROM law_changes ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@app.post("/api/generate-report")
def generate_report():
    conn = sqlite3.connect("laws.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, url, date, description FROM law_changes ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=400, detail="Нет данных для анализа")

    changes_data = [
        {"title": r[0], "url": r[1], "date": r[2], "description": r[3]}
        for r in rows
    ]

    report_text = _make_report(changes_data)

    return {
        "report_text": report_text,
        "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    }

@app.get("/")
def root():
    return {"message": "Бэкенд AI-помощника Газпромнефть-ЦР запущен!"}