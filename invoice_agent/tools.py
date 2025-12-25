from dataclasses import dataclass

from pydantic_ai import RunContext

from service_layer.invoice_service import get_invoice_infos


@dataclass
class MyDeps:
    db_name: str
    is_admin: bool


def get_invoice_details(ctx: RunContext[MyDeps], invoice_number: str) -> str:
    """Fetches invoice details from the billing system.

    :param ctx: Context injected into chat
    :type ctx: RunContext[MyDeps]
    :param invoice_number: Invoice number provided by the user
    :type invoice_number: str
    :return: invoice details as a string
    :rtype: str
    """
    # Simulate fetching invoice details
    db_data = get_invoice_infos(invoice_number)

    if not db_data:
        return f"No database record found for Invoice ID: {invoice_number}"

    return db_data


def USD_to_EUR_converter(amount_usd: float) -> float:
    """Converts an amount from USD to EUR.

    :param amount_usd: Amount in USD
    :type amount_usd: float
    :return: Equivalent amount in EUR
    :rtype: float
    """
    conversion_rate = 0.85
    amount_eur = amount_usd * conversion_rate
    return round(amount_eur, 2)
