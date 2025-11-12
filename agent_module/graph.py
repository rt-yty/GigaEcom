from typing import TypedDict, Annotated, Any, cast

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from .llm import system_prompt
from .tools import llm_with_tools, tools

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("messages"),
])

chain = prompt | llm_with_tools

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def agent_node(state: State):
    result = await chain.ainvoke({"messages": state["messages"]})
    return {"messages": [result]}

tool_node = ToolNode(tools)

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_conditional_edges("agent", tools_condition,
                            {"tools": "tools", "__end__": END})
graph.add_edge("tools", "agent")
graph.set_entry_point("agent")

memory = MemorySaver()
app = graph.compile(checkpointer=memory)
