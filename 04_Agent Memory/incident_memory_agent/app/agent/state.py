from langgraph.graph import MessagesState


class AgentState(MessagesState):
    memory_context: str
