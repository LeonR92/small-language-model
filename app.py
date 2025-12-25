import os
from dataclasses import dataclass
from enum import StrEnum
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL, USER_PROMPT
from customer_detail_agent.agent import customer_detail_agent
from invoice_agent.agent import invoice_agent
from ticket_agent.agent import ticket_agent

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")


@dataclass
class MyDeps:
    db_name: str
    is_admin: bool


model = MistralModel(AI_MODEL)


planner_agent = Agent(
    model,
    deps_type=MyDeps,
    system_prompt=(
        """You are a smart router.
        
        # RULES OF THOUGHT
        1. First, identify the ENTITY: Is it a Ticket or an Invoice?
        2. Second, identify the INTENT: Is it a status check or a value lookup?
        3. Third, SELECT the tool that best matches the ENTITY and INTENT.
        
        If no ID is provided, reject the request. DO NOT GUESS.
        """
    ),
)


class AgentNames(StrEnum):
    TICKET_AGENT = "ticket_worker"
    INVOICE_AGENT = "invoice_worker"
    CUSTOMER_DETAIL_AGENT = "customer_detail_worker"
    NONE = "none"


class PlannerOutput(BaseModel):
    """
    The internal decision-making schema for the Router.
    """

    decision: str = Field(
        description="The reasoning behind the agent's choice of tool."
    )
    target_agent: AgentNames = Field(description="The classification of the request.")
    tools_called: List[str] = Field(
        default_factory=list,
        description="The names of the tools the agent decided to invoke.",
    )
    final_summary: str = Field(
        description="The final answer derived from the tool output."
    )


@planner_agent.tool
async def delegate_to_customer_detail_worker(
    ctx: RunContext[MyDeps], customer_id: str | None, email_address: str | None
) -> str:
    """Delegates the task of retrieving customer details to a specialized worker.

    :param ctx: context injected into chat
    :type ctx: RunContext[MyDeps]
    :param customer_id: customer's ID
    :type customer_id: str
    :return: output from the worker agent
    :rtype: str
    """
    if email_address:
        instruction = f"Retrieve details for customer email: {email_address}"
    else:
        instruction = f"Retrieve details for customer ID: {customer_id}"
    # The planner hands over the context to the worker
    result = await customer_detail_agent.run(instruction, deps=ctx.deps)
    return result.output


@planner_agent.tool
async def delegate_to_ticket_search_worker(
    ctx: RunContext[MyDeps], ticket_number: str
) -> str:
    """Delegates the task of searching for a ticket to a specialized worker.

    :param ctx: context injected into chat
    :type ctx: RunContext[MyDeps]
    :param ticket_number: Ticket number provided by the user, starting with TKT
    :type ticket_number: str
    :return: output from the worker agent
    :rtype: str
    """
    # The planner hands over the context to the worker
    result = await ticket_agent.run(ticket_number, deps=ctx.deps)
    return result.output


@planner_agent.tool
async def delegate_to_invoice_search_worker(
    ctx: RunContext[MyDeps], invoice_number: str
) -> str:
    """Delegates the task of searching for an invoice starting with INV- to a specialized worker.

    :param ctx: context injected into chat
    :type ctx: RunContext[MyDeps]
    :param invoice_number: Invoice number provided by the user
    :type invoice_number: str
    :return: output from the worker agent
    :rtype: str
    """
    # The planner hands over the context to the worker
    result = await invoice_agent.run(invoice_number, deps=ctx.deps)
    return result.output


if __name__ == "__main__":
    my_db_deps = MyDeps(db_name="Production_SQL_Azure", is_admin=True)
    result = planner_agent.run_sync(
        USER_PROMPT, deps=my_db_deps, output_type=PlannerOutput
    )
    print(result.output)
