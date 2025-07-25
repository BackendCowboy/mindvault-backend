from pydantic import BaseModel


class JournalReflectionRequest(BaseModel):
    entry: str
    mood: str


class JournalReflectionResponse(BaseModel):
    reflection: str
