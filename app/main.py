from app.models import Message


from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas import ChatRequest, ChatResponse, HistoryResponse, HistoryRequest
from app.ai_client import get_ai_response, get_streaming_response
from app.crud import save_message, get_last_messages
from app.prompts import build_system_prompt
from app.prompt_builder import build_messages

app = FastAPI(title="Study Buddy Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    return {"Hello": "World","status": "ok" }

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db:Session = Depends(get_db)):
    print("request received", request)
    # save user messages
    save_message(db, request.user_id, 'user', request.message)

    # Fetch past messages
    history = get_last_messages(db, request.user_id, limit=10)
    history = list[Message](reversed[Message](history))
        
    print('history', history)

    # get reply from ai modal
    ai_response = get_ai_response(request.message)

    # save the response

    save_message(db, request.user_id, 'assistant', ai_response)

    return ChatResponse(reply = ai_response)
    
@app.post("/chat_history", response_model=HistoryResponse)
def chat_history(request:HistoryRequest, db:Session = Depends(get_db)):
    # Fetch past messages
    history = get_last_messages(db, request.user_id, limit=100)
    return {
        "messages": history
    }

@app.get("/chats", response_model=HistoryResponse)
def get_chats(user_id:str, db:Session = Depends(get_db)):
    # Fetch past messages
    chats = get_last_messages(db, user_id, limit=100)
    return {
        "messages": chats
    }

@app.post("/chat_streams")
def chat_streams(request: ChatRequest, db: Session = Depends(get_db)):
    # Save user message
    save_message(db, request.user_id, 'user', request.message)

    # Fetch history
    history = get_last_messages(db, request.user_id, limit=8)
    history = list[Message](reversed(history))

    # Build system prompt
    system_prompt = build_system_prompt(
        mode=request.mode,
        format_type=request.format
    )

    # Build final messages
    messages = build_messages(
        system_prompt=system_prompt,
        history=history,
        user_message=request.message
    )
    
    # Create a generator that collects the full response and saves it
    def stream_with_save():
        full_response = ""
        for chunk in get_streaming_response(messages):
            full_response += chunk
            yield chunk
        
        # Save the complete AI response after streaming is done
        save_message(db, request.user_id, 'assistant', full_response)
    
    return StreamingResponse(
        stream_with_save(),
        media_type="text/plain"
    )

print(__name__)

# if __name__ == "__main__":
#     print("Starting server...")
#     uvicorn.run(app, host="0.0.0.0", port=PORT)
