from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
import uuid

from database import init_db
from schemas import ChatMessage, ChatResponse
from agent_module.graph import app as agent_app
from api import routers

app = FastAPI(title="Giga Agent API")


@app.on_event("startup")
async def startup_event():
    await init_db()
    print("База данных инициализирована")


for router in routers:
    app.include_router(router)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
):
    thread_id = message.thread_id or str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    human_message = HumanMessage(content=message.message)
    
    try:
        result = await agent_app.ainvoke(
            {"messages": [human_message]},
            config=config
        )

        last_message = result["messages"][-1]
        response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        return ChatResponse(response=response_text, thread_id=thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка агента: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Giga Agent API"}
