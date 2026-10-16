"""Basket pricing. Settings come from config.json next to this file."""
import json
import os

with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    CONFIG = json.load(f)


def tax_for(subtotal):
    # Tax settings now live in a nested "tax" block so regions can disable tax.
    tax = CONFIG["tax"]
    if not tax.get("enabled", True):
        return 0.0
    return round(subtotal * tax["rate"], 2)


def quote(items):
    subtotal = round(sum(i["price"] * i["qty"] for i in items), 2)
    tax = tax_for(subtotal)
    return {
        "currency": CONFIG["currency"],
        "subtotal": subtotal,
        "tax": tax,
        "total": round(subtotal + tax, 2),
    }
