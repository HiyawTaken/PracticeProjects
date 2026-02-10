# I am building this project to understand the basics of pydantic and fastAPI

from datetime import date
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workouts: List["WorkoutOut"] = []
next_id = 1

class WorkoutCreate(BaseModel):
    date: date
    exercise: str
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(ge=0)

    @field_validator("exercise")
    @classmethod
    def exercise_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("exercise cannot be blank")
        return v


class WorkoutOut(WorkoutCreate):
    id: int


@app.post("/workouts", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
def create_workout(workout: WorkoutCreate):
    global next_id
    new_workout = WorkoutOut(id=next_id, **workout.model_dump())
    next_id += 1
    workouts.append(new_workout)
    return new_workout


@app.get("/workouts", response_model=List[WorkoutOut])
def read_workouts():
    return workouts


@app.get("/workouts/{workout_id}", response_model=WorkoutOut)
def read_workout(workout_id: int):
    for w in workouts:
        if w.id == workout_id:
            return w
    raise HTTPException(status_code=404, detail=f"Workout {workout_id} not found")


@app.put("/workouts/{workout_id}", response_model=WorkoutOut)
def update_workout(workout_id: int, updated: WorkoutCreate):
    for i, w in enumerate(workouts):
        if w.id == workout_id:
            replaced = WorkoutOut(id=workout_id, **updated.model_dump())
            workouts[i] = replaced
            return replaced
    raise HTTPException(status_code=404, detail=f"Workout {workout_id} not found")


@app.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int):
    for i, w in enumerate(workouts):
        if w.id == workout_id:
            workouts.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Workout {workout_id} not found")
