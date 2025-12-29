from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from requests import Session
from sqlalchemy.orm import session
from app.database import SessionLocal
from app.schemas import ChatRequest, ChatResponse, HistoryResponse, HistoryRequest
from app.ai_client import get_ai_response, get_streaming_response
from app.crud import save_message, get_last_messages

app = FastAPI(title="Study Buddy Backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def read_root():
    return {"Hello": "World","status": "ok" }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db:Session = Depends(get_db)):
    print("request received", request)
    # save user messages
    save_message(db, request.user_id, 'user', request.message)

    # Fetch past messages
    history = get_last_messages(db, request.user_id, limit=10)

    print('history', history)

    # get reply from ai modal
    ai_response = get_ai_response(request.message)

    # save the response

    save_message(db, request.user_id, 'agent', ai_response)

    return ChatResponse(reply = ai_response)
    
@app.post("/chat_history", response_model=HistoryResponse)
def chat_history(request:HistoryRequest, db:Session = Depends(get_db)):
    # Fetch past messages
    history = get_last_messages(db, request.user_id, limit=10)
    return {
        "messages": history
    }

@app.get("/chats", response_model=HistoryResponse)
def get_chats(user_id:str, db:Session = Depends(get_db)):
    # Fetch past messages
    chats = get_last_messages(db, user_id, limit=10)
    return {
        "messages": chats
    }

@app.post("/chat_streams")
def chat_streams(request: ChatRequest):
    return StreamingResponse(
        get_streaming_response(request.message),
        media_type="text/plain"
    )

print(__name__)

# if __name__ == "__main__":
#     print("Starting server...")
#     uvicorn.run(app, host="0.0.0.0", port=PORT)
