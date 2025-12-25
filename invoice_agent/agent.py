import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

from config import AI_MODEL
from dependencies import MyDeps
from invoice_agent.prompt import invoice_agent_prompt
from invoice_agent.tools import USD_to_EUR_converter, get_invoice_details

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")


model = MistralModel(AI_MODEL)


class InvoiceOutputModel(BaseModel):
    """Represents the output model for invoice-related queries."""

    found: bool = Field(description="Indicates if the  invoice was found")
    details: Optional[str] = Field(description="Details about the invoice")


invoice_agent = Agent(
    model,
    system_prompt=(invoice_agent_prompt),
    deps_type=MyDeps,
    output_type=InvoiceOutputModel,
)

invoice_agent.tool(get_invoice_details)
invoice_agent.tool_plain(USD_to_EUR_converter)
