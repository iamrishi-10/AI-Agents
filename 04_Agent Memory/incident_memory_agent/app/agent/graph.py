from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.tools import get_recent_logs, get_service_health
from app.config.settings import LLM_MODEL, OPENAI_KEY
from app.db.database import AsyncSessionLocal
from app.services.memory_service import retrieve_memories

TOOLS = [get_service_health, get_recent_logs]

model = ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_KEY).bind_tools(TOOLS)


def _latest_user_text(state: AgentState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return message.content
    return state["messages"][-1].content


def _format_memories(memories) -> str:
    if not memories:
        return ""

    lines = "\n".join(f"- {memory.content}" for memory in memories)
    return f"Previous relevant incidents:\n{lines}"


async def retrieve_memory(state: AgentState, config: RunnableConfig) -> dict:
    """Retrieve similar memories for this user/service and stash them as context."""
    user_id = config["configurable"]["user_id"]
    service_name = config["configurable"]["service_name"]

    query = _latest_user_text(state)

    async with AsyncSessionLocal() as session:
        memories = await retrieve_memories(
            session,
            user_id=user_id,
            service_name=service_name,
            query=query,
        )

    return {"memory_context": _format_memories(memories)}


def call_model(state: AgentState) -> dict:
    """Invoke the tool-bound model over the current messages (+ memory context, if any)."""
    messages = state["messages"]

    memory_context = state.get("memory_context")
    if memory_context:
        messages = [
            SystemMessage(
                content=(
                    f"Relevant memory context:\n{memory_context}\n\n"
                    "Treat retrieved memory as historical context only. "
                    "Validate current incident causes using current tool evidence."
                )
            ),
            *messages,
        ]

    response = model.invoke(messages)

    return {"messages": [response]}


tool_node = ToolNode([get_service_health, get_recent_logs])

graph_builder = StateGraph(AgentState)
graph_builder.add_node("retrieve_memory", retrieve_memory)
graph_builder.add_node("call_model", call_model)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "retrieve_memory")
graph_builder.add_edge("retrieve_memory", "call_model")
graph_builder.add_conditional_edges("call_model", tools_condition)
graph_builder.add_edge("tools", "call_model")

graph = graph_builder.compile()
