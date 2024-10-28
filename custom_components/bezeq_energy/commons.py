"""Common methods for Bezeq Energy."""

from my_bezeq import Invoice


def get_last_invoice(invoices: list[Invoice]) -> Invoice | None:
    """Get the last invoice by InvoiceNumber."""
    if not invoices:
        return None
    # Sort invoices by InvoiceNumber and return the last one
    sorted_invoices = sorted(invoices, key=lambda inv: inv.invoice_number)
    return sorted_invoices[-1]
