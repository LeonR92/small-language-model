from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from ai_model import model
from customer_detail_agent.prompt import customer_detail_prompt
from customer_detail_agent.tools import get_customer_details
from dependencies import MyDeps


class CustomerDetailsAgentOutput(BaseModel):
    """
    Structured response including the internal reasoning process.
    """

    found: bool = Field(description="Indicates if customer details was found")
    details: Optional[str] = Field(description="Details about customer")


customer_detail_agent = Agent(
    model,
    system_prompt=customer_detail_prompt,
    deps_type=MyDeps,
    output_type=CustomerDetailsAgentOutput,
)


customer_detail_agent.tool(get_customer_details)
