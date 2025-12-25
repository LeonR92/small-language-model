import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL
from dependencies import MyDeps
from ticket_agent.prompt import ticket_agent_prompt
from ticket_agent.tools import get_ticket_details

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")


model = MistralModel(AI_MODEL)


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
