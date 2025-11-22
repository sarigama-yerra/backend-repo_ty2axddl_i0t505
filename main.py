import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Profile, Workout, Reaction, Comment

app = FastAPI(title="Gym Social Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_str_id(doc):
    if not doc:
        return doc
    d = doc.copy()
    if d.get("_id"):
        d["id"] = str(d.pop("_id"))
    return d

# Root
@app.get("/")
def read_root():
    return {"message": "Gym Social Tracker Backend running"}

# Health/database test
@app.get("/test")
def test_database():
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "collections": []
    }
    try:
        if db is not None:
            status["database"] = "✅ Connected"
            status["collections"] = db.list_collection_names()[:10]
    except Exception as e:
        status["database"] = f"⚠️ {str(e)[:80]}"
    return status

# Profiles
@app.post("/api/profiles", response_model=dict)
def create_profile(profile: Profile):
    try:
        new_id = create_document("profile", profile)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/profiles/{user_id}")
def get_profile(user_id: str):
    try:
        doc = db["profile"].find_one({"user_id": user_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Profile not found")
        return to_str_id(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workouts
@app.post("/api/workouts", response_model=dict)
def create_workout(workout: Workout):
    try:
        new_id = create_document("workout", workout)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class FeedItem(BaseModel):
    id: str
    type: str  # workout | reaction | comment
    user_id: str
    performed_at: Optional[datetime] = None
    workout: Optional[dict] = None
    meta: Optional[dict] = None

@app.get("/api/feed", response_model=List[FeedItem])
def get_feed(limit: int = 20):
    try:
        workouts = db["workout"].find().sort("performed_at", -1).limit(limit)
        items: List[FeedItem] = []
        for w in workouts:
            item = FeedItem(
                id=str(w["_id"]),
                type="workout",
                user_id=w.get("user_id", ""),
                performed_at=w.get("performed_at"),
                workout=to_str_id(w),
            )
            items.append(item)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reactions
@app.post("/api/reactions", response_model=dict)
def add_reaction(r: Reaction):
    try:
        new_id = create_document("reaction", r)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Comments
@app.post("/api/comments", response_model=dict)
def add_comment(c: Comment):
    try:
        new_id = create_document("comment", c)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
