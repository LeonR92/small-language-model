import os
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL, SYSTEM_PROMPT, USER_PROMPT
from service_layer.customer_details import get_customer_info
from service_layer.invoice_service import get_invoice_infos
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

    found: bool = Field(description="Indicates if the ticket or invoice was found")
    details: Optional[str] = Field(description="Details about the ticket or invoice")


ticket_agent = Agent(
    model, system_prompt=SYSTEM_PROMPT, deps_type=MyDeps, output_type=OutputModel
)

customer_detail_agent = Agent(
    model, system_prompt=SYSTEM_PROMPT, deps_type=MyDeps, output_type=OutputModel
)

invoice_agent = Agent(
    model,
    system_prompt=(
        """You are an invoice agent that retrieves invoice details based on user requests.
    Always ensure to fetch the latest data from the billing system and present it clearly. Invoice amount is USD per default.
    You can also convert USD to EUR using the provided tool.
    """
    ),
    deps_type=MyDeps,
    output_type=OutputModel,
)

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


@ticket_agent.tool
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


@invoice_agent.tool
def get_invoice_details(ctx: RunContext[MyDeps], invoice_number: str) -> str:
    """Fetches invoice details from the billing system.

    :param ctx: Context injected into chat
    :type ctx: RunContext[MyDeps]
    :param invoice_number: Invoice number provided by the user
    :type invoice_number: str
    :return: invoice details as a string
    :rtype: str
    """
    # Simulate fetching invoice details
    db_data = get_invoice_infos(invoice_number)

    if not db_data:
        return f"No database record found for Invoice ID: {invoice_number}"

    return db_data


@invoice_agent.tool_plain
def USD_to_EUR_converter(amount_usd: float) -> float:
    """Converts an amount from USD to EUR.

    :param amount_usd: Amount in USD
    :type amount_usd: float
    :return: Equivalent amount in EUR
    :rtype: float
    """
    conversion_rate = 0.85
    amount_eur = amount_usd * conversion_rate
    return round(amount_eur, 2)


@customer_detail_agent.tool
def get_customer_details(
    ctx: RunContext[MyDeps], customer_id: str | None, email_address: str | None
) -> str:
    """Fetches customer details including invoice and ticket information from the customer database.
    Use this to get extended customer information

    :param ctx: context injected into chat
    :type ctx: RunContext[MyDeps]
    :param customer_id: customer ID provided by the user
    :type customer_id: str
    :return: customer detail
    :rtype: str
    """
    db_data = get_customer_info(customer_id, email_address)
    if not db_data:
        return f"No database record found for Customer ID: {customer_id}"
    return db_data


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
    :param ticket_number: Ticket number provided by the user
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
    """Delegates the task of searching for an invoice to a specialized worker.

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
