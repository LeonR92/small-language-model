import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL, SYSTEM_PROMPT, USER_PROMPT

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")


@dataclass
class MyDeps:
    db_name: str
    is_admin: bool


model = MistralModel(AI_MODEL)

agent = Agent(model, system_prompt=SYSTEM_PROMPT, deps_type=MyDeps)


class TicketDetails(BaseModel):
    ticket_id: str = Field(
        # Regex: Starts with TKT-, followed by 1 or more digits
        pattern=r"^TKT-\d+$",
        description="The unique identifier for the ticket. Must follow the format 'TKT-' followed by numbers.",
        examples=["TKT-1001", "TKT-9999"],
    )
    reason: str = Field(description="A concise explanation of the customer's problem")
    confidence_level: float = Field(
        ge=0,
        le=1,
        description="How certain the tool is about this data, from 0.0 to 1.0, with 0.0 being not confident at all 1.0 very confident",
    )


@agent.tool
def get_ticket_details(ctx: RunContext[MyDeps], ticket_id: str) -> TicketDetails:
    """
    Retrieves official system records for a specific customer support ticket.

    This tool is the ONLY authoritative source for ticket status, history, and
    original customer descriptions. Call this tool immediately whenever a user
    provides a ticket identifier or asks about the status of a specific issue.

    Args:
        ctx: The runtime context containing database connection dependencies.
        ticket_id: The alphanumeric ticket identifier. Must follow the format
            'TKT-' followed by 4 or more digits (e.g., 'TKT-1001').

    Returns:
        A TicketDetails object containing the validated database record.

    Raises:
        ValueError: If the ticket_id format is invalid or not found in the database.
    """
    # Note: Ensure your return matches the type hint TicketDetails, not a string!
    # Mocking the database fetch here:
    return TicketDetails(
        ticket_id=ticket_id,
        reason="Poor internet connection in the North East region.",
        confidence_level=1.0,
    )


if __name__ == "__main__":
    my_db_deps = MyDeps(db_name="Production_SQL_Azure", is_admin=True)

    result = agent.run_sync(
        USER_PROMPT,
        deps=my_db_deps,
    )
    print(result.output)
