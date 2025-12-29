from pydantic import BaseModel
from typing import List
from datetime import datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

class HistoryRequest(BaseModel):
    user_id:str

class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True   # 👈 CRITICAL (Pydantic v2)


class HistoryResponse(BaseModel):
    messages: List[MessageResponse]