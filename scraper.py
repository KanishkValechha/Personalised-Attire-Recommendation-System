import os
import re
import time
import requests
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# CSV file to save metadata
CSV_FILE = os.path.join(DATA_DIR, "products.csv")

SEARCH_QUERY = "oversized tshirts men"
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service)

# Check if header is needed (i.e. file doesn't exist or is empty)
write_header = not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0

# Open CSV file in append mode so that data is not overwritten
csv_file = open(CSV_FILE, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
if write_header:
    csv_writer.writerow([
        "product_id", "product_name", "category", "price", "product_url",
        "description", "front_image_url", "model_image_url", "additional_images"
    ])

def extract_image_url(style_attr):
    """Extract URL from a style attribute like:
    background-image: url("https://assets.myntassets.com/...");
    """
    match = re.search(r'url\(["\']?(.*?)["\']?\)', style_attr)
    return match.group(1) if match else None

try:
    driver.get("https://www.myntra.com/")
    time.sleep(3)
    
    search_box = driver.find_element(By.CSS_SELECTOR, "input.desktop-searchBar")
    search_box.clear()
    search_box.send_keys(SEARCH_QUERY)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    # Example: Scrape one page first (later, implement pagination as needed)
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

    print(f"Found {len(product_links)} products.")

    for idx, link in enumerate(product_links, start=1):
        print(f"\nProcessing product {idx}: {link}")
        driver.get(link)
        time.sleep(3)
        
        # Extract basic metadata: title, description, price, etc.
        try:
            title = driver.find_element(By.CSS_SELECTOR, ".pdp-title").text
        except Exception:
            title = "N/A"
        try:
            description = driver.find_element(By.CSS_SELECTOR, 
                                                ".pdp-product-description-content").text
        except Exception:
            description = "N/A"
        try:
            price = driver.find_element(By.CSS_SELECTOR, ".pdp-price").text
        except Exception:
            price = "N/A"
        
        # Example for category: you might infer it from the breadcrumb or URL
        category = "Shirt"  # You might refine this extraction
        
        product_id = f"product_{idx}"  # Or parse it from the URL if available
        
        # Extract front image (if available)
        try:
            front_image_element = driver.find_element(By.CSS_SELECTOR, "img.pdp-main-image")
            front_image_url = front_image_element.get_attribute("src")
        except Exception:
            front_image_url = None
        
        # Extract model image from image grid (as discussed earlier)
        try:
            container = driver.find_element(By.CSS_SELECTOR,
                                              ".image-grid-container.common-clearfix")
            image_divs = container.find_elements(By.CSS_SELECTOR, ".image-grid-image")
            if image_divs:
                model_image_div = image_divs[-1]
                style_attr = model_image_div.get_attribute("style")
                model_image_url = extract_image_url(style_attr)
            else:
                model_image_url = None
        except Exception as e:
            print("Error extracting model image:", e)
            model_image_url = None
        
        # Optionally, collect additional images from the image grid
        additional_images = []
        try:
            container = driver.find_element(By.CSS_SELECTOR,
                                              ".image-grid-container.common-clearfix")
            image_divs = container.find_elements(By.CSS_SELECTOR, ".image-grid-image")
            for div in image_divs:
                style_attr = div.get_attribute("style")
                img_url = extract_image_url(style_attr)
                if img_url:
                    additional_images.append(img_url)
        except Exception:
            additional_images = []

        # Download images if needed (or store the URLs to download later)
        if front_image_url:
            try:
                img_data = requests.get(front_image_url).content
                img_filename = os.path.join(IMAGES_DIR, f"{product_id}_front.jpg")
                with open(img_filename, "wb") as f:
                    f.write(img_data)
                # Optionally update the URL to a local path if you plan to use local images.
            except Exception as e:
                print("Failed to download front image:", e)

        if model_image_url:
            try:
                img_data = requests.get(model_image_url).content
                img_filename = os.path.join(IMAGES_DIR, f"{product_id}_model.jpg")
                with open(img_filename, "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print("Failed to download model image:", e)

        # Write the data to CSV
        csv_writer.writerow([
            product_id,
            title,
            category,
            price,
            link,
            description,
            front_image_url,
            model_image_url,
            ";".join(additional_images)
        ])
finally:
    csv_file.close()
    driver.quit()
