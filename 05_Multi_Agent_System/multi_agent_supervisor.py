import os 
from dotenv import load_dotenv
from typing import NotRequired, Literal, TypedDict
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
MODEL = "gpt-5.4-mini"



class MultiAgentState(TypedDict):
    user_request: str

    research_summary: NotRequired[str]
    code_result: NotRequired[str]

    next_agent: NotRequired[
        Literal["research", "coding", "finish"]
    ]

    turn_count: int


class RouteDecision(BaseModel):
    next_agent: Literal["research", "coding", "finish"]

    reason: str = Field(
        description="Short explanation for the routing decision."
    )



base_model = ChatOpenAI(
    model=MODEL,
    api_key=OPENAI_API_KEY,
)

supervisor_model = base_model.with_structured_output(RouteDecision)



def supervisor(state: MultiAgentState) -> dict:
    research = state.get("research_summary", "NOT_COMPLETED")
    code = state.get("code_result", "NOT_COMPLETED")

    prompt = f"""
    user_request:
    {state["user_request"]}

    research_status:
    {research}

    coding_status:
    {code}

    Decide which agent should act next.
    
    
    Routing rules:

    1. If research_summary is NOT_COMPLETED:
    choose "research".

    2. If research_summary is completed AND code_result is NOT_COMPLETED:
    choose "coding".

    3. Only choose "finish" when code_result is completed.

    Do not choose finish just because the research output appears to contain code.
    The coding agent must always produce the implementation.
"""


    decision = supervisor_model.invoke(
        [
            SystemMessage(
            content= "You are a supervisor coordinating specialist agents. "
                    "Route work rather than performing specialist work yourself."
            ),
            HumanMessage(content = prompt),
        ]

    )
    print(
    f"\n[SUPERVISOR] → {decision.next_agent}"
    f"\nReason: {decision.reason}")

    return {
        "next_agent": decision.next_agent,
        "turn_count": state["turn_count"] + 1,
    }


def research_agent(state: MultiAgentState) -> dict:
    response = base_model.invoke(
        [
            SystemMessage(
                content=(
            "You are a technical research specialist. "
            "Return only requirements, architecture, constraints, "
            "and implementation guidance for the coding specialist. "
            "Do not output Python code, pseudocode, or a final implementation. "
            "The coding specialist is solely responsible for implementation."
                )
            ),
            HumanMessage(content=state["user_request"]),
        ]
    )

    print("\n[RESEARCH AGENT]")
    print(response.content)

    return {
        "research_summary": response.content,
    }




def coding_agent(state: MultiAgentState) -> dict:
    research = state.get(
        "research_summary",
        "No research was required.",
    )

    prompt = f"""
User request:
{state["user_request"]}

Research supplied by the research specialist:
{research}

Produce the requested implementation.

Keep the implementation concise and explain important
technical decisions briefly.
"""

    response = base_model.invoke(
        [
            SystemMessage(
                content=(
                    "You are a Python coding specialist. "
                    "Your responsibility is implementation."
                )
            ),
            HumanMessage(content=prompt),
        ]
    )

    print("\n[CODING AGENT]")
    print(response.content)

    return {
        "code_result": response.content,
    }

MAX_TURNS = 6


def route_supervisor(
    state: MultiAgentState,
) -> Literal["research", "coding", "finish"]:
    # Deterministic safety limit around LLM routing
    if state["turn_count"] >= MAX_TURNS:
        print("\nMaximum agent turns reached.")
        return "finish"

    return state["next_agent"]



def finish(state: MultiAgentState) -> dict:
    print("\n========== FINAL RESULT ==========")

    if state.get("code_result"):
        print(state["code_result"])

    elif state.get("research_summary"):
        print(state["research_summary"])

    else:
        print("No specialist result was produced.")

    return {}

builder = StateGraph(MultiAgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("research", research_agent)
builder.add_node("coding", coding_agent)
builder.add_node("finish", finish)


builder.add_edge(
    START,
    "supervisor",
)


builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "research": "research",
        "coding": "coding",
        "finish": "finish",
    },
)


builder.add_edge(
    "research",
    "supervisor",
)

builder.add_edge(
    "coding",
    "supervisor",
)

builder.add_edge(
    "finish",
    END,
)


graph = builder.compile()



if __name__ == "__main__":
    result = graph.invoke(
        {
            "user_request": (
                """
            Explain how Multi Agents System Works in Production. Using a Python Example         
            """
            ),
            "turn_count": 0,
        }
    )

    print("\n========== WORKFLOW COMPLETE ==========")