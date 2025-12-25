from pydantic import BaseModel, ConfigDict, Field

from database import Customer, CustomerDetail, Invoice, Session


class CustomerDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Customer ID")
    address: str = Field(description="Customer's address")
    phone_number: str = Field(description="Customer's phone number")
    country: str = Field(description="Customer's country")
    city: str = Field(description="Customer's city")
    is_vip: int = Field(default=0, description="VIP status (0 = No, 1 = Yes)")


def get_customer_info(
    customer_id: str | None, email_address: str | None
) -> CustomerDetails | None:
    """Get customer details by customer ID or email address.xwww

    :param customer_id: The ID of the customer.
    :type customer_id: str | None
    :param email_address: The email address of the customer.
    :type email_address: str | None
    :return: The details of the customer or None if not found.
    :rtype: CustomerDetails | None
    """
    session = Session()
    if email_address:
        row = (
            session.query(CustomerDetail)
            .join(Customer, CustomerDetail.customer_id == Customer.id)
            .join(Invoice, Invoice.customer_id == Customer.id)
            .filter(Customer.email == email_address)
            .first()
        )
    else:
        row = (
            session.query(CustomerDetail)
            .join(Customer, CustomerDetail.customer_id == Customer.id)
            .filter(Customer.id == customer_id)
            .first()
        )

    if not row:
        return None
    return CustomerDetails.model_validate(row, from_attributes=True)
