from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from database import Customer, Session, Ticket


class TicketDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_number: str = Field(
        pattern=r"^TKT-\d+$",
        description="The unique identifier for the ticket, e.g., TKT-1001.",
        examples=["TKT-1001"],
    )
    customer_name: str = Field(
        description="The full name of the customer who raised the ticket."
    )
    customer_email: str = Field(description="The customer's contact email.")
    status: str = Field(
        description="The current lifecycle status of the ticket (e.g., Open, Resolved)."
    )
    created_at: datetime = Field(
        description="The timestamp when the ticket was created."
    )


def get_ticket_infos(ticket_number: str):
    session = Session()
    row = (
        session.query(
            Ticket.ticket_number,
            Ticket.status,
            Ticket.created_at,
            Customer.name.label("customer_name"),
            Customer.email.label("customer_email"),
        )
        .join(Customer, Ticket.customer_id == Customer.id)
        .filter(Ticket.ticket_number == ticket_number)
        .first()
    )

    if not row:
        return None
    return TicketDetails.model_validate(row, from_attributes=True)
