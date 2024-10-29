"""Common methods for Bezeq Energy."""

from datetime import date

from my_bezeq import BaseCardDetails, Invoice, ServiceType


def get_last_invoice(invoices: list[Invoice]) -> Invoice | None:
    """Get the last invoice by InvoiceNumber."""
    if not invoices:
        return None
    # Sort invoices by InvoiceNumber and return the last one
    sorted_invoices = sorted(invoices, key=lambda inv: inv.invoice_number)
    return sorted_invoices[-1]


def translate_date_period(date_period: str) -> str:
    """Format date_period string to standard (comparable) date."""
    # Define mapping for Hebrew months to their respective month numbers
    hebrew_months = {
        "ינואר": "01",
        "פברואר": "02",
        "מרץ": "03",
        "אפריל": "04",
        "מאי": "05",
        "יוני": "06",
        "יולי": "07",
        "אוגוסט": "08",
        "ספטמבר": "09",
        "אוקטובר": "10",
        "נובמבר": "11",
        "דצמבר": "12",
    }

    # Split the input to extract year and month
    parts = date_period.split()
    year = parts[0]
    month_name = parts[1]

    # Get the month number from the Hebrew month name
    month = hebrew_months.get(month_name)
    if not month:
        msg = f"Unknown Hebrew month: {month_name}"
        raise ValueError(msg)

    # Format as "YYYY-MM"
    return f"{year}-{month}"


def translate_date_to_date_period(date_period: date) -> str:
    """Format date to standard (comparable) date."""
    return date_period.strftime("%Y-%m")


def get_card_by_service_type(cards: list, service_type: ServiceType) -> BaseCardDetails:
    """Extract Card Data from Tab by service type."""
    card = next(filter(lambda card: card.service_type == service_type, cards), None)
    if card is None:
        msg = f"Card {service_type} not found"
        raise ValueError(msg)
    return card.card_details
