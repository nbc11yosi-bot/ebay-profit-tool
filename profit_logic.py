import requests
from shipping_module import load_shipping_table, get_shipping_cost
from profit_calc import calculate_profit_rate

def fetch_usd_to_jpy_rate() -> float:
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = response.json()
        return float(data["rates"]["JPY"])
    except Exception as e:
        print("為替レート取得失敗:", e)
        return 145.00  # フォールバック値

df = load_shipping_table()

def calculate_profit(item_type, weight, insured, cost_price, usd_price, usd_to_jpy):
    target_price = int(usd_price * usd_to_jpy)
    shipping_cost = get_shipping_cost(weight, "USA", item_type, insured, df)
    if shipping_cost == -1:
        return None, "該当する送料が見つかりません"

    result = calculate_profit_rate(cost_price, shipping_cost, 0.20, target_price)
    result.update({
        "usd_price": usd_price,
        "target_price": target_price,
        "shipping_cost": shipping_cost,
        "exchange_rate": usd_to_jpy
    })
    return result, None

def suggest_min_usd_price(item_type, weight, insured, cost_price, usd_to_jpy):
    shipping_cost = get_shipping_cost(weight, "USA", item_type, insured, df)
    if shipping_cost == -1:
        return None, "該当する送料が見つかりません"

    total_cost = cost_price + shipping_cost
    min_price_jpy = int(total_cost / 0.8)
    min_price_usd = round(min_price_jpy / usd_to_jpy, 2)
    return min_price_usd, None