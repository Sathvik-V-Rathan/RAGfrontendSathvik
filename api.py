from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from main import agent # Correctly imports agent and its configuration
from langchain_core.messages import HumanMessage
import os

app = FastAPI()

# Make sure static directory exists
os.makedirs("static", exist_ok=True)

# Mount the static directory to serve CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        initial_state = {"messages": [HumanMessage(content=request.query)]}
        result = agent.invoke(initial_state)
        
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            return {"response": last_message.content}
        else:
            return {"response": "(No response generated)"}
    except Exception as e:
        return {"response": f"Error processing request: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
