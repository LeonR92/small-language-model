from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from database import Customer, Invoice, Session


class InvoiceDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invoice_number: str = Field(
        pattern=r"^INV-\d+-[A-Za-z]+$",
        description="The unique identifier for the invoice, e.g., INV-02398-JM.",
        examples=["INV-02398-JM"],
    )
    customer_name: str = Field(
        description="The full name of the customer associated with the invoice."
    )
    customer_email: str = Field(description="The customer's contact email.")
    amount: float = Field(description="The total amount due on the invoice.")
    issued_date: datetime = Field(description="The date when the invoice was issued.")
    due_date: datetime = Field(
        description="The date when the payment for the invoice is due."
    )


def get_invoice_infos(invoice_number: str):
    session = Session()
    row = (
        session.query(
            Invoice.invoice_number,
            Invoice.amount,
            Invoice.due_date,
            Invoice.issued_date,
            Customer.name.label("customer_name"),
            Customer.email.label("customer_email"),
        )
        .join(Customer, Invoice.customer_id == Customer.id)
        .filter(Invoice.invoice_number == invoice_number)
        .first()
    )

    if not row:
        return None
    return InvoiceDetails.model_validate(row, from_attributes=True)
