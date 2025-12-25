from pydantic_ai import RunContext

from dependencies import MyDeps
from service_layer.ticket_service import TicketDetails, get_ticket_infos


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
