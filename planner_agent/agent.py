from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from ai_model import model
from dependencies import MyDeps
from planner_agent.prompt import planner_agent_prompt
from planner_agent.tools import (
    delegate_to_customer_detail_worker,
    delegate_to_invoice_search_worker,
    delegate_to_ticket_search_worker,
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


planner_agent = Agent(
    model,
    system_prompt=planner_agent_prompt,
    deps_type=MyDeps,
    output_type=PlannerOutput,
)


planner_agent.tool(delegate_to_customer_detail_worker)
planner_agent.tool(delegate_to_ticket_search_worker)
planner_agent.tool(delegate_to_invoice_search_worker)
