import pandas as pd
import os
import sys

def resource_path(relative_path):
    """PyInstallerでバンドルされたファイルのパスを取得"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def load_shipping_table(csv_path: str = "shipping_rates.csv") -> pd.DataFrame:
    full_path = resource_path(csv_path)
    return pd.read_csv(full_path)

def get_shipping_cost(weight: int, region: str, item_type: str, insured: bool, df: pd.DataFrame) -> int:
    match = df[
        (df["region"].str.lower() == region.lower()) &
        (df["type"].str.lower() == item_type.lower()) &
        (df["weight_min"] <= weight) &
        (df["weight_max"] >= weight)
    ]
    if match.empty:
        return -1

    base_price = int(match.iloc[0]["base_price"])
    insurance_fee = int(match.iloc[0]["insurance_price"]) if insured else 0
    return base_price + insurance_fee