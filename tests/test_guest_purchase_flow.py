from src.flows.purchase_flow import (PurchaseFlows)
from src.utils.logger import get_logger

logger = get_logger("test_guest_purchase_flow")

def test_guest_purchase_flow(browser_page, test_data):
    page = browser_page
    base_url = test_data["base_url"]
    cart_url = test_data.get("cart_url")
    query = test_data["query"]
    max_price = test_data["max_price"]
    limit = test_data["limit"]

    PurchaseFlows.guest_purchase_flow(
        page=page,
        query=query,
        max_price=max_price,
        limit=limit,
        base_url=base_url,
        cart_url=cart_url
    )