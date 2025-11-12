import uuid

from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage

from .db.session import init_db
from .schemas import ChatMessage, ChatResponse
from .agent.graph import app as agent_app
from .api.routes import product_router, category_router

app = FastAPI(title="Giga Agent API")


@app.on_event("startup")
async def startup_event():
    await init_db()
    print("База данных инициализирована")


app.include_router(product_router)
app.include_router(category_router)


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
