from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from ai_model import model
from dependencies import MyDeps
from ticket_agent.prompt import ticket_agent_prompt
from ticket_agent.tools import get_ticket_details


class TicketAgentOutput(BaseModel):
    """
    Structured response including the internal reasoning process.
    """

    found: bool = Field(description="Indicates if the ticket or invoice was found")
    details: Optional[str] = Field(description="Details about the ticket or invoice")


ticket_agent = Agent(
    model,
    system_prompt=ticket_agent_prompt,
    deps_type=MyDeps,
    output_type=TicketAgentOutput,
)


ticket_agent.tool(get_ticket_details)
