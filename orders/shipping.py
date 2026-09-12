import os

from dotenv import load_dotenv

load_dotenv()

SHIPPING_FEE = int(os.getenv("SHIPPING_FEE"))
FREE_SHIPPING_THRESHOLD = int(os.getenv("FREE_SHIPPING_THRESHOLD"))


def calculate_shipping_fee(subtotal):
    """
    小計がFREE_SHIPPING_THRESHOLD以上なら送料無料、
    それ以外は固定送料SHIPPING_FEEを返す。
    """
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING_FEE
