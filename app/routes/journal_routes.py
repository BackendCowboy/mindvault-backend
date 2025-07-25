# app/journal_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from collections import Counter, defaultdict
from app.schemas.journal_schemas import JournalEntryCreate, JournalEntryResponse
from fastapi import Request
from app.limiter import limiter
from app.ai.openai_utils import ask_gpt as generate_ai_response

from app.models import JournalEntry, JournalEntryUpdate
from app.database import engine
from app.auth import get_current_user

router = APIRouter(tags=["Journal"])


@router.post("/journals")
@limiter.limit("5/minute")
def create_journal(
    entry: JournalEntryCreate,
    request: Request,
    user=Depends(get_current_user),
):
    with Session(engine) as session:
        # 🧠 Generate reflection using GPT
        try:
            prompt = f"Reflect on the following journal entry:\n\nTitle: {entry.title}\nMood: {entry.mood}\nContent:\n{entry.content}"
            reflection = generate_ai_response(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI reflection failed: {e}")

        # 📦 Save journal + reflection
        new_entry = JournalEntry(
            title=entry.title,
            content=entry.content,
            mood=entry.mood,
            reflection=reflection,
            user_id=user.id,
        )
        session.add(new_entry)
        session.commit()
        session.refresh(new_entry)
        return {"message": "Entry saved with reflection", "entry": new_entry}


@router.get("/journals", response_model=List[JournalEntryResponse])
def get_journals(user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = (
            select(JournalEntry)
            .where(JournalEntry.user_id == user.id)
            .order_by(JournalEntry.created_at.desc())
        )
        return session.exec(statement).all()


@router.get("/journals/{entry_id}", response_model=JournalEntryResponse)
def get_journal(entry_id: int, user=Depends(get_current_user)):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user.id:
            raise HTTPException(status_code=404, detail="Entry not found")
        return entry


@router.put("/journals/{entry_id}")
def update_journal(
    entry_id: int,
    updated: JournalEntryUpdate,
    user=Depends(get_current_user),
):
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


@router.delete("/journals/{entry_id}")
def delete_journal(entry_id: int, user=Depends(get_current_user)):
    with Session(engine) as session:
        entry = session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user.id:
            raise HTTPException(status_code=404, detail="Entry not found")
        session.delete(entry)
        session.commit()
        return {"message": f"Entry {entry_id} deleted"}


@router.get("/journals/filter", response_model=List[JournalEntryResponse])
def filter_journals(
    user=Depends(get_current_user),
    mood: Optional[str] = Query(None, description="Filter by mood"),
    search: Optional[str] = Query(None, description="Search in title/content"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO)"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
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
            raise HTTPException(
                status_code=404, detail="No entries match the given filters"
            )
        return results


@router.get("/journals/mood-summary")
def get_mood_summary(
    user=Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    with Session(engine) as session:
        stmt = (
            select(JournalEntry.mood, func.count(JournalEntry.id))
            .where(JournalEntry.user_id == user.id)
            .group_by(JournalEntry.mood)
        )
        if start_date:
            stmt = stmt.where(JournalEntry.created_at >= start_date)
        if end_date:
            stmt = stmt.where(JournalEntry.created_at <= end_date)

        results = session.exec(stmt).all()
        return {"summary": {mood: count for mood, count in results}}


@router.get("/journals/mood-trends")
def get_mood_trends(user=Depends(get_current_user)):
    with Session(engine) as session:
        entries = session.exec(
            select(JournalEntry)
            .where(JournalEntry.user_id == user.id)
            .order_by(JournalEntry.created_at)
        ).all()

    mood_trends = defaultdict(lambda: defaultdict(int))
    for e in entries:
        if e.mood:
            day = e.created_at.date().isoformat()
            mood_trends[day][e.mood] += 1

    return [
        {"date": day, "moods": counts} for day, counts in sorted(mood_trends.items())
    ]


@router.get("/journals/streak")
def get_journal_streak(user=Depends(get_current_user)):
    with Session(engine) as session:
        dates = sorted(
            {
                ent.created_at.date()
                for ent in session.exec(
                    select(JournalEntry.created_at).where(
                        JournalEntry.user_id == user.id
                    )
                ).all()
            }
        )

    if not dates:
        return {"current_streak": 0, "longest_streak": 0}

    longest = current = 1
    today = datetime.utcnow().date()
    for prev, curr in zip(dates, dates[1:]):
        if (curr - prev).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    if (today - dates[-1]).days > 1:
        current = 0

    return {"current_streak": current, "longest_streak": longest}


@router.get("/journals/stats")
def get_journal_stats(user=Depends(get_current_user)):
    with Session(engine) as session:
        entries = session.exec(
            select(JournalEntry).where(JournalEntry.user_id == user.id)
        ).all()

    if not entries:
        return {"message": "No journal entries found."}

    total = len(entries)
    words = sum(len(e.content.split()) for e in entries)
    moods = [e.mood for e in entries if e.mood]
    most_common = Counter(moods).most_common(1)
    return {
        "total_entries": total,
        "first_entry": min(e.created_at for e in entries),
        "latest_entry": max(e.created_at for e in entries),
        "total_words": words,
        "average_words_per_entry": round(words / total, 2),
        "most_common_mood": most_common[0][0] if most_common else None,
    }


@router.get("/journals/7-day-summary")
def seven_day_summary(user=Depends(get_current_user)):
    today = datetime.utcnow().date()
    last_week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    with Session(engine) as session:
        entries = session.exec(
            select(JournalEntry).where(
                JournalEntry.user_id == user.id,
                JournalEntry.created_at >= today - timedelta(days=6),
            )
        ).all()

    summary = {d.isoformat(): {"count": 0, "moods": {}} for d in last_week}
    for e in entries:
        d = e.created_at.date().isoformat()
        grp = summary[d]
        grp["count"] += 1
        grp["moods"][e.mood or "unspecified"] = (
            grp["moods"].get(e.mood or "unspecified", 0) + 1
        )

    return {"last_7_days": summary}
