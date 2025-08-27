def calculate_profit_rate(
    cost_price: int,
    shipping_cost: int,
    ebay_fee_rate: float,
    target_price: int,
    min_margin: float = 5.0,
    max_margin: float = 20.0
) -> dict:
    """
    利益率を計算し、指定範囲内かどうかを判定する関数

    Parameters:
        cost_price (int): 仕入れ価格（メルカリ）
        shipping_cost (int): 送料
        ebay_fee_rate (float): eBay手数料（例：0.20）
        target_price (int): eBayでの販売予定価格
        min_margin (float): 最低利益率（%）
        max_margin (float): 最大利益率（%）

    Returns:
        dict: 利益率、利益額、総コスト、出品可否などを含む結果
    """
    ebay_fee = int(target_price * ebay_fee_rate)
    total_cost = cost_price + shipping_cost + ebay_fee
    profit = target_price - total_cost
    profit_rate = (profit / total_cost * 100) if total_cost > 0 else 0

    return {
        "cost_price": cost_price,
        "shipping_cost": shipping_cost,
        "ebay_fee": ebay_fee,
        "total_cost": total_cost,
        "target_price": target_price,
        "profit": profit,
        "profit_rate": round(profit_rate, 2),
        "is_profitable": min_margin <= profit_rate <= max_margin
    }