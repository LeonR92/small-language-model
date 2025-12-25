from pydantic_ai import RunContext

from customer_detail_agent.agent import customer_detail_agent
from dependencies import MyDeps
from invoice_agent.agent import invoice_agent
from ticket_agent.agent import ticket_agent


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
