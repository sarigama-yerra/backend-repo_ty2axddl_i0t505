"""
Database Schemas for Gym Social Tracker

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Profile(BaseModel):
    user_id: str = Field(..., description="Unique user id or handle")
    name: str = Field(..., description="Display name")
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    goal: Optional[str] = Field(None, description="strength | aesthetics | fitness")
    avatar_url: Optional[str] = None

class ExerciseSet(BaseModel):
    reps: int = Field(..., ge=1, le=100)
    weight: Optional[float] = Field(None, ge=0)

class Exercise(BaseModel):
    name: str
    sets: List[ExerciseSet]

class Workout(BaseModel):
    user_id: str
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    duration_min: Optional[int] = Field(None, ge=1, le=600)
    notes: Optional[str] = None
    exercises: List[Exercise] = Field(default_factory=list)

class Reaction(BaseModel):
    workout_id: str
    user_id: str
    type: str = Field(..., description="like | fire | clap | star")

class Comment(BaseModel):
    workout_id: str
    user_id: str
    text: str
