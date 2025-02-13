import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"
if not os.path.exists("images"):
    os.makedirs("images")
SEARCH_QUERY = "shirt"
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://www.myntra.com/")
    time.sleep(3)
    search_box = driver.find_element(By.CSS_SELECTOR, "input.desktop-searchBar")
    search_box.clear()
    search_box.send_keys(SEARCH_QUERY)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    product_cards = driver.find_elements(By.CSS_SELECTOR, "li.product-base")
    product_links = []
    for card in product_cards:
        try:
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            if link not in product_links:
                product_links.append(link)
        except Exception as e:
            print("Error fetching product link:", e)
            continue
    print(f"Found {len(product_links)} products for '{SEARCH_QUERY}'.")
    for idx, link in enumerate(product_links, start=1):
        print(f"\nProcessing product {idx}: {link}")
        driver.get(link)
        time.sleep(3)
        try:
            model_image_element = driver.find_element(By.CSS_SELECTOR, ".model-img")
            model_image_url = model_image_element.get_attribute("src")
        except Exception as e:
            print("No model image found or error:", e)
            model_image_url = None
        try:
            description_element = driver.find_element(By.CSS_SELECTOR, ".pdp-description")
            description = description_element.text
        except Exception as e:
            print("No description found or error:", e)
            description = "N/A"
        print("Model image URL:", model_image_url)
        print("Product Description:", description)
        if model_image_url:
            try:
                image_data = requests.get(model_image_url).content
                filename = os.path.join("images", f"product_{idx}.jpg")
                with open(filename, "wb") as f:
                    f.write(image_data)
                print("Downloaded image to", filename)
            except Exception as e:
                print("Failed to download image:", e)
finally:
    driver.quit()
