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
agent = Agent(model, system_prompt=SYSTEM_PROMPT, deps_type=MyDeps)


class OutputModel(BaseModel):
    confidence_level: float = Field(ge=0, le=1)
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


if __name__ == "__main__":
    my_db_deps = MyDeps(db_name="Production_SQL_Azure", is_admin=True)
    result = agent.run_sync(USER_PROMPT, deps=my_db_deps, output_type=OutputModel)
    if not result.output.ticket_found:
        print("ticket not found")
    print(result.output)
