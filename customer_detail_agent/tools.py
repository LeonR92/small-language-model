from pydantic_ai import RunContext

from dependencies import MyDeps
from service_layer.customer_details import get_customer_info


def get_customer_details(
    ctx: RunContext[MyDeps], customer_id: str | None, email_address: str | None
) -> str:
    """Fetches customer details including invoice and ticket information from the customer database.
    Use this to get extended customer information

    :param ctx: context injected into chat
    :type ctx: RunContext[MyDeps]
    :param customer_id: customer ID provided by the user
    :type customer_id: str
    :return: customer detail
    :rtype: str
    """
    db_data = get_customer_info(customer_id, email_address)
    if not db_data:
        return f"No database record found for Customer ID: {customer_id}"
    return db_data
