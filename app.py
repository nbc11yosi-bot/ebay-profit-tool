from flask import Flask, render_template, request
from mercari_scraper import extract_mercari_info
from profit_logic import fetch_usd_to_jpy_rate, calculate_profit, suggest_min_usd_price
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    info_list = []
    profit_result = None
    error = None
    exchange_rate = fetch_usd_to_jpy_rate()

    if request.method == "POST":
        urls = request.form.get("urls", "").splitlines()
        cost_price = request.form.get("cost_price", "")
        usd_price = request.form.get("usd_price", "")
        item_type = request.form.get("item_type", "small_packet")
        weight = request.form.get("weight", "750")
        insured = request.form.get("insured") == "on"

        for url in urls:
            url = url.strip()
            if url:
                info = extract_mercari_info(url)
                info_list.append(info)

        try:
            if cost_price and usd_price:
                profit_result, error = calculate_profit(
                    item_type,
                    int(weight),
                    insured,
                    int(cost_price),
                    float(usd_price),
                    exchange_rate
                )
        except Exception as e:
            error = str(e)

    return render_template("index.html",
                           info_list=info_list,
                           profit_result=profit_result,
                           error=error,
                           exchange_rate=exchange_rate)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)