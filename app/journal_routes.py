from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func 
from collections import Counter, defaultdict

from app.models import JournalEntry, UserCreate, UserRead, JournalEntryUpdate
from app.database import engine
from app.auth import (
    get_current_user,
    register_user,
    authenticate_user,
    create_access_token,
)
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

# -------------------------------
#          JOURNAL ROUTES
# -------------------------------

# ✅ Create journal entry
@router.post("/journals")
def create_journal(entry: JournalEntry, user=Depends(get_current_user)):
    with Session(engine) as session:
        entry.user_id = user.id  # Attach to current user
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return {"message": "Entry saved", "entry": entry}


# ✅ Get all journal entries (basic list, newest first)
@router.get("/journals", response_model=List[JournalEntry])
def get_journals(user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = (
            select(JournalEntry)
            .where(JournalEntry.user_id == user.id)
            .order_by(JournalEntry.created_at.desc())
        )
        return session.exec(statement).all()


# ✅ Get one journal by ID (with user ownership check)
@router.get("/journals/{entry_id}", response_model=JournalEntry)
def get_journal(entry_id: int, user=Depends(get_current_user)):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user.id:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry


# ✅ Update journal entry
@router.put("/journals/{entry_id}")
def update_journal(entry_id: int, updated: JournalEntryUpdate, user=Depends(get_current_user)):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user.id:
            raise HTTPException(status_code=404, detail="Entry not found")

        entry.title = updated.title
        entry.content = updated.content
        entry.mood = updated.mood
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return {"message": f"Entry {entry_id} updated", "entry": entry}


# ✅ Delete journal entry
@router.delete("/journals/{entry_id}")
def delete_journal(entry_id: int, user=Depends(get_current_user)):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user.id:
            raise HTTPException(status_code=404, detail="Entry not found")

        session.delete(entry)
        session.commit()
        return {"message": f"Entry {entry_id} deleted"}


# ✅ Advanced filtering route: moods, search, dates, pagination
@router.get("/journals/filter", response_model=List[JournalEntry])
def filter_journals(
    user=Depends(get_current_user),
    mood: Optional[str] = Query(None, description="Filter by mood"),
    search: Optional[str] = Query(None, description="Search in title/content"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    with Session(engine) as session:
        statement = select(JournalEntry).where(JournalEntry.user_id == user.id)

        if mood:
            statement = statement.where(JournalEntry.mood == mood)
        if search:
            pattern = f"%{search.lower()}%"
            statement = statement.where(
                JournalEntry.title.ilike(pattern) | JournalEntry.content.ilike(pattern)
            )
        if start_date:
            statement = statement.where(JournalEntry.created_at >= start_date)
        if end_date:
            statement = statement.where(JournalEntry.created_at <= end_date)

        statement = statement.order_by(JournalEntry.created_at.desc())
        statement = statement.offset(offset).limit(limit)

        results = session.exec(statement).all()

        if not results:
            raise HTTPException(status_code=404, detail="No entries match the given filters")

        return results
    
    # ✅ Mood summary route
@router.get("/journals/mood-summary")
def get_mood_summary(
    user=Depends(get_current_user),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)")
):
    with Session(engine) as session:
        statement = (
            select(JournalEntry.mood, func.count(JournalEntry.id))
            .where(JournalEntry.user_id == user.id)
            .group_by(JournalEntry.mood)
        )

        if start_date:
            statement = statement.where(JournalEntry.created_at >= start_date)
        if end_date:
            statement = statement.where(JournalEntry.created_at <= end_date)

        results = session.exec(statement).all()

        summary = {mood: count for mood, count in results}

        return {"summary": summary}
    
 
    #  Returns mood trends over time for the logged-in user.
    # Groups journal entries by date and mood, showing how often each mood occurred per day.

@router.get("/journals/mood-trends")
def get_mood_trends(user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = (
            select(JournalEntry)
            .where(JournalEntry.user_id == user.id)
            .order_by(JournalEntry.created_at)
        )
        entries = session.exec(statement).all()

        mood_trends = defaultdict(lambda: defaultdict(int))

        for entry in entries:
            if entry.mood:
                day = entry.created_at.date().isoformat()
                mood_trends[day][entry.mood] += 1

        # Transform the nested dict into a list of {date, mood_counts}
        trend_data = [
            {
                "date": day,
                "moods": moods
            }
            for day, moods in sorted(mood_trends.items())
        ]

        return trend_data
    
@router.get("/journals/streak")
def get_journal_streak(user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = (
            select(JournalEntry.created_at)
            .where(JournalEntry.user_id == user.id)
            .order_by(JournalEntry.created_at.asc())
        )
        entries = session.exec(statement).all()

        if not entries:
            return {"current_streak":0, "longest_streak":0}
        
        # Convert all datetimes to just dates
        dates = sorted({entry.date() for entry in entries})

        longest_streak = 1 
        current_streak = 1
        today = datetime.utcnow().date()

        for i in range(1, len(dates)):
            delta = (dates[i] - dates [i - 1]).days
            if delta == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            elif delta > 1:
                current_streak = 1

        # Check if the latest entry is not today 
        if (today - dates[-1]).days > 1:
            current_streak = 0
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak
        }
    
    # -- Smart Journal Stats ---
@router.get("/journals/stats")
def get_journal_stats(user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(JournalEntry).where(JournalEntry.user_id == user.id)
        entries = session.exec(statement).all()

        if not entries:
            return {"message": "No journal entries found."}

        total_entries = len(entries)
        created_dates = [entry.created_at for entry in entries]
        moods = [entry.mood for entry in entries if entry.mood]
        total_words = sum(len(entry.content.split()) for entry in entries)
        average_words = total_words / total_entries if total_entries > 0 else 0

        mood_count = Counter(moods)
        most_common_mood = mood_count.most_common(1)[0][0] if mood_count else None

        return {
            "total_entries": total_entries,
            "first_entry": min(created_dates),
            "latest_entry": max(created_dates),
            "total_words": total_words,
            "average_words_per_entry": round(average_words, 2),
            "most_common_mood": most_common_mood
        }
    
    # -- 7 day Summary Inisght Logic --

@router.get("/journals/7-day-summary")
def seven_day_summary(user=Depends(get_current_user)):
     with Session(engine) as session:
        today = datetime.utcnow().date()
        last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

        # Get all entries from the last 7 days
        statement = (
            select(JournalEntry)
            .where(
                JournalEntry.user_id == user.id,
                JournalEntry.created_at >= today - timedelta(days=6)
            )
        )
        entries = session.exec(statement).all()

        summary = {day.isoformat(): {"count": 0, "moods": {}} for day in last_7_days}

        for entry in entries:
            entry_date = entry.created_at.date().isoformat()
            if entry_date in summary:
                summary[entry_date]["count"] += 1
                mood = entry.mood or "unspecified"
                summary[entry_date]["moods"][mood] = summary[entry_date]["moods"].get(mood, 0) + 1

        return {"last_7_days": summary}





# -------------------------------
#          AUTH ROUTES
# -------------------------------

# ✅ Register a new user
@router.post("/register", response_model=UserRead)
def register(user: UserCreate):
    return register_user(user)


# ✅ Login user and return Bearer token
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}