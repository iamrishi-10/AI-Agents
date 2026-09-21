import asyncio

from dotenv import load_dotenv

from agents import Agent, Runner, trace

load_dotenv()

billing_agent = Agent(
    name="Billing Agent",
    handoff_description=(
        "Handles billing issues such as duplicate charges, refunds, invoices, "
        "and subscription payment problems."
    ),
    instructions=(
        "You are a billing support specialist. Help the user resolve billing "
        "issues such as duplicate charges, incorrect invoices, or subscription "
        "payment problems."
    ),
)

technical_agent = Agent(
    name="Technical Agent",
    handoff_description=(
        "Handles technical issues such as API errors, timeouts, outages, "
        "and integration problems."
    ),
    instructions=(
        "You are a technical support specialist. Help the user resolve "
        "technical issues such as API errors, timeouts, outages, or "
        "integration problems."
    ),
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Classify the user's support issue and hand it off "
        "to the correct specialist. "
        "Do not solve billing or technical problems yourself."
    ),
    handoffs=[
        billing_agent,
        technical_agent,
    ],
)


async def run_case(user_input: str) -> None:
    with trace("Support Triage"):
        result = await Runner.run(
            triage_agent,
            user_input,
            max_turns=5,
        )

    print(result.final_output)
    print(result.last_agent.name)


async def main() -> None:
    await run_case("I was charged twice for the same subscription.")
    print("---")
    await run_case("The API keeps returning timeout errors.")


if __name__ == "__main__":
    asyncio.run(main())
