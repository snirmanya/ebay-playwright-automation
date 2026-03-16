import re


def parse_price(price_text: str) -> float | None:
    if not price_text:
        return None

    cleaned = price_text.replace(",", "")
    match = re.search(r"(\d+(\.\d+)?)", cleaned)
    if not match:
        return None

    return float(match.group(1))