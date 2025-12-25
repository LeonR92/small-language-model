from pydantic import BaseModel, ConfigDict, Field

from database import Customer, CustomerDetail, Invoice, Session, Ticket


class UniversalCustomerDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Customer ID")
    address: str = Field(description="Customer's address")
    phone_number: str = Field(description="Customer's phone number")
    country: str = Field(description="Customer's country")
    city: str = Field(description="Customer's city")
    is_vip: int = Field(default=0, description="VIP status (0 = No, 1 = Yes)")

    invoice_number: str = Field(description="The unique identifier for the invoice.")
    amount: float = Field(description="The total amount of the invoice.")
    due_date: str = Field(description="The due date for the invoice payment.")
    created_at: str = Field(description="The timestamp when the invoice was created.")

    ticket_number: str = Field(description="The unique identifier for the ticket.")
    ticket_status: str = Field(description="The current status of the ticket.")
    ticket_created_at: str = Field(
        description="The timestamp when the ticket was created."
    )


def get_customer_info(
    customer_id: str | None, email_address: str | None
) -> UniversalCustomerDetails | None:

    with Session() as session:  # Use 'with' to prevent connection leaks
        query = (
            session.query(CustomerDetail, Invoice, Customer, Ticket)
            .join(Customer, CustomerDetail.customer_id == Customer.id)
            .outerjoin(Invoice, Invoice.customer_id == Customer.id)
            .outerjoin(Ticket, Ticket.customer_id == Customer.id)
        )

        if email_address:
            row = query.filter(Customer.email == email_address).first()
        else:
            row = query.filter(Customer.id == customer_id).first()

        if not row:
            return None

        # UNPACK the tuple
        cust_detail, invoice, cust, ticket = row

        # FLATTEN into a dictionary that matches UniversalCustomerDetails
        flattened_data = {
            # From CustomerDetail
            "id": cust_detail.id,
            "address": cust_detail.address,
            "phone_number": cust_detail.phone_number,
            "country": cust_detail.country,
            "city": cust_detail.city,
            "is_vip": cust_detail.is_vip,
            # From Invoice
            "invoice_number": invoice.invoice_number,
            "amount": invoice.amount,
            "due_date": str(invoice.due_date),
            "created_at": str(invoice.issued_date),
            # From Ticket
            "ticket_number": ticket.ticket_number,
            "ticket_status": ticket.status,
            "ticket_created_at": str(ticket.created_at),
        }

        return UniversalCustomerDetails.model_validate(flattened_data)
