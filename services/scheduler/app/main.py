from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from ...task_database import models
import schemas
from database import SessionLocal, engine

app = FastAPI(
    title="TaskerAI: Scheduler",
    description="This module add new task to user scheduleer",
    version="0.1.0"
)

def calculate_duration(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds()

# TODO
# Сделал файл заглушку, нужно будет заменить на нормальную db
def get_db():
    db = SessionLocal() # Нужно откуда подсасоывать локальную ссесию
    try:
        yield db
    finally:
        db.close()

@app.post("/reschedule-tasks", response_model=List[models.Task])
def reschedule_tasks(request: schemas.RescheduleRequest, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter(
        models.Task.user_name == request.user_name,
        models.Task.start_time >= request.start_from,
        models.Task.status != "completed"
    ).all()

    if not tasks:
        return []
    
    for task in tasks:
        if task.estimated_duration:
            task.duration = task.estimated_duration.total_seconds()
        else:
            task.duration = 3600

    tasks.sort(key=lambda x: (
        -x.priority, 
        x.min_start_time if x.min_start_time else datetime.min
    ))


    current_time = request.start_from
    scheduled_tasks = []

    for task in tasks:
        start_time = max(current_time, task.min_start_time) if task.min_start_time else current_time
        end_time = start_time + timedelta(seconds=task.duration)
        
        task.planned_start = start_time
        task.planned_end = end_time
        
        current_time = end_time
        scheduled_tasks.append(task)
    try:
        for task in scheduled_tasks:
            db.merge(task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")

    return scheduled_tasks