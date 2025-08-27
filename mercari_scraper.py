def extract_mercari_info(url: str) -> dict:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    from googletrans import Translator
    from PIL import Image
    import pytesseract
    import re
    import os

    # Tesseract設定
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.environ["TESSDATA_PREFIX"] = os.path.join(os.getcwd(), "tessdata")

    price_source = "不明"

    def extract_price_from_image(image_path="mercari_screenshot.png"):
        nonlocal price_source
        try:
            text = pytesseract.image_to_string(Image.open(image_path), lang='jpn')
            match = re.search(r'(¥|RM|\$)?\s*([0-9]+(?:\.[0-9]+)?)', text)
            if match:
                raw_price = match.group(2).replace(",", "").replace(" ", "")
                price_source = "OCR"
                return float(raw_price)
        except Exception as e:
            print("OCR価格取得失敗:", e)
        return "不明"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=ja")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        driver.save_screenshot("mercari_screenshot.png")
        with open("mercari_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # 商品名
        name_tag = soup.find("h1")
        name = name_tag.text.strip() if name_tag else "不明"

        # 商品状態
        condition = "不明"
        condition_label = soup.find("div", string=lambda s: s and "商品の状態" in s)
        if condition_label:
            next_div = condition_label.find_next_sibling("div")
            if next_div:
                condition = next_div.text.strip()

        # 商品状態の英訳
        condition_map = {
            "新品": "Brand New",
            "未使用に近い": "Like New",
            "目立った傷や汚れなし": "Very Good",
            "やや傷や汚れあり": "Good",
            "傷や汚れあり": "Acceptable",
            "全体的に状態が悪い": "Poor"
        }
        translated_condition = condition_map.get(condition, "Unknown")

        # 商品名の英訳
        translator = Translator()
        try:
            translated_name = translator.translate(name, src='ja', dest='en').text
        except Exception:
            translated_name = "Unknown"

        # 画像URL抽出
        image_tags = soup.find_all("img", src=lambda s: s and "https://static.mercdn.net" in s)
        seen = set()
        image_urls = []
        for tag in image_tags:
            src = tag.get("src")
            if src and src not in seen:
                seen.add(src)
                image_urls.append(src)

        # 価格取得（HTML → OCR補完）
        price = "不明"
        html_text = ""
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'¥') or contains(text(),'RM') or contains(text(),'$')]"))
            )
            html_text = price_element.text
        except Exception:
            html_text = soup.get_text()

        match = re.search(r'(¥|RM|\$)?\s*([0-9,.]+)', html_text)
        if match:
            raw_price = match.group(2).replace(",", "").replace(" ", "")
            try:
                price = float(raw_price)
                price_source = "HTML"
            except ValueError:
                price = extract_price_from_image()
        else:
            price = extract_price_from_image()

    finally:
        driver.quit()

    return {
        "name": name,
        "translated_name": translated_name,
        "condition": condition,
        "translated_condition": translated_condition,
        "price": price,
        "image_urls": image_urls,
        "source_url": url,
        "price_source": price_source
    }