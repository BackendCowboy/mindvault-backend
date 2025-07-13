from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated

from app.ai.openai_utils import ask_gpt as generate_ai_response
from app.schemas.openai_schemas import JournalReflectionRequest, JournalReflectionResponse
from app.auth import get_current_user  # make sure this import works for JWT

router = APIRouter(prefix="/api/ai", tags=["AI"])

# Existing generic GPT prompt route
class AIRequest(BaseModel):
    prompt: str

@router.post("/respond")
async def ai_respond(request: AIRequest):
    try:
        response = generate_ai_response(request.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New AI Reflection route
@router.post("/reflect", response_model=JournalReflectionResponse)
async def reflect_on_journal(
    data: JournalReflectionRequest,
    user: Annotated[dict, Depends(get_current_user)]
):
    try:
        prompt = (
            f"You are a warm and emotionally intelligent journaling guide. A user just wrote:\n\n"
            f"\"{data.entry}\"\n\n"
            f"Mood: {data.mood}\n\n"
            f"Give a short, thoughtful reflection or follow-up question to help them reflect further. "
            f"Be gentle, supportive, and human."
        )

        response = generate_ai_response(prompt)
        return JournalReflectionResponse(reflection=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reflection failed: {str(e)}")