SHIPPING_FEE = 500
FREE_SHIPPING_THRESHOLD = 5000


def calculate_shipping_fee(subtotal):
    """
    小計がFREE_SHIPPING_THRESHOLD以上なら送料無料、
    それ以外は固定送料SHIPPING_FEEを返す。
    """
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING_FEE
