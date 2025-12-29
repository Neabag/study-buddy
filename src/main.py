import os
from typing import Union

import uvicorn
from fastapi import FastAPI

app = FastAPI()

# PORT = int(os.getenv("PORT", 8080))


@app.get("/health")
def read_root():
    return {"Hello": "World","status": "ok" }

@app.post("/chat")
def chat(request: dict):
    print("request received", request)
    return {"message": "AI received your message.."}


print(__name__)

# if __name__ == "__main__":
#     print("Starting server...")
#     uvicorn.run(app, host="0.0.0.0", port=PORT)
