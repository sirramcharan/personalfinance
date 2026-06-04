"""Formatting utilities for Indian financial context."""

import datetime


def format_inr(amount: float, show_symbol: bool = True) -> str:
    """Format amount in Indian numbering system with Rs symbol."""
    if show_symbol:
        prefix = "Rs "
    else:
        prefix = ""
    
    amount = abs(amount)
    if amount >= 10000000:
        crores = amount / 10000000
        return f"{prefix}{crores:,.2f} Cr"
    elif amount >= 100000:
        lakhs = amount / 100000
        return f"{prefix}{lakhs:,.2f} L"
    elif amount >= 1000:
        thousands = amount / 1000
        return f"{prefix}{thousands:,.2f}K"
    else:
        return f"{prefix}{amount:,.2f}"


def format_currency_plain(amount: float) -> str:
    """Format as plain comma-separated number."""
    return f"{amount:,.2f}"


def get_period_label(month_offset: int) -> str:
    """Convert month offset to readable label like 'Month 1 (Jan 2026)'."""
    base_date = datetime.datetime.now()
    target = base_date + datetime.timedelta(days=month_offset * 30)
    return f"M{month_offset} ({target.strftime('%b %Y')})"
