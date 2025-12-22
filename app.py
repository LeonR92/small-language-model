import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL, SYSTEM_PROMPT, USER_PROMPT
from service_layer.ticket_service import TicketDetails, get_ticket_infos

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")


@dataclass
class MyDeps:
    db_name: str
    is_admin: bool


model = MistralModel(AI_MODEL)


class OutputModel(BaseModel):
    """
    Structured response including the internal reasoning process.
    """

    confidence_level: float = Field(ge=0, le=1)
    ticket_found: bool
    message: str


agent = Agent(
    model, system_prompt=SYSTEM_PROMPT, deps_type=MyDeps, output_type=OutputModel
)

planner_agent = Agent(
    model,
    deps_type=MyDeps,
    system_prompt=(
        "You are a Lead Controller. Your job is to: "
        "1. Reason about the user's request. "
        "2. Create a plan. "
        "3. Delegate the lookup to the 'search_agent'. "
        "4. Summarize the findings into the required output format."
    ),
)


class FinalResponse(BaseModel):
    chain_of_thought: str = Field(
        description="A step-by-step internal monologue of how the ticket was analyzed."
    )
    plan_executed: str
    ticket_found: bool
    message: str


@agent.tool
def get_ticket_details(ctx: RunContext[MyDeps], ticket_number: str) -> TicketDetails:
    """Retrieves complete official records for a support ticket.
    Mandatory to use this to find customer contact info, ticket status, and creation dates.

    :param ctx: Context injected into chat
    :type ctx: RunContext[MyDeps]
    :param ticket_number: Ticket number provided by the user
    :type ticket_number: str
    :raises ValueError: Error if ticket number is not found
    :return: ticket details from the database
    :rtype: TicketDetails
    """
    db_data = get_ticket_infos(ticket_number)

    if not db_data:
        return f"No database record found for Ticket ID: {ticket_number}"

    return db_data


@planner_agent.tool
async def delegate_to_search_worker(ctx: RunContext[MyDeps], user_goal: str) -> str:
    """Passes a specific data task to the search specialist."""
    # The planner hands over the context to the worker
    result = await agent.run(user_goal, deps=ctx.deps)
    return result.output


if __name__ == "__main__":
    my_db_deps = MyDeps(db_name="Production_SQL_Azure", is_admin=True)
    result = planner_agent.run_sync(
        USER_PROMPT, deps=my_db_deps, output_type=FinalResponse
    )
    if not result.output.ticket_found:
        print("ticket not found")
    print(result.output)
