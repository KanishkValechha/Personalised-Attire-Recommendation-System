import pandas as pd
import requests
import cv2
import mediapipe as mp
import numpy as np
import io
import os
from urllib.parse import urlparse

INPUT_CSV_PATH = './data/pae_dataset.csv'
OUTPUT_CSV_PATH = './data/myntra_data_updated.csv'

UPPER_BODY_LANDMARKS = [mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
                        mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
LOWER_BODY_LANDMARKS = [mp.solutions.pose.PoseLandmark.LEFT_ANKLE,
                        mp.solutions.pose.PoseLandmark.RIGHT_ANKLE,
                        mp.solutions.pose.PoseLandmark.LEFT_HEEL,
                        mp.solutions.pose.PoseLandmark.RIGHT_HEEL]
VISIBILITY_THRESHOLD = 0.6

mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=True,
                             model_complexity=1,
                             min_detection_confidence=0.5)

def is_full_body_image(image_url):
    if not image_url or not isinstance(image_url, str):
        print(f"Skipping invalid URL: {image_url}")
        return False

    try:
        parsed_url = urlparse(image_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
             print(f"Skipping malformed URL: {image_url}")
             return False
    except ValueError:
        print(f"Skipping invalid URL format: {image_url}")
        return False

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(image_url, stream=True, timeout=15, headers=headers)
        response.raise_for_status()

        image_data = io.BytesIO(response.content)
        image_np = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), cv2.IMREAD_COLOR)

        if image_np is None:
            print(f"Failed to decode image from URL: {image_url}")
            return False

        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

        results = pose_detector.process(image_rgb)

        if not results.pose_landmarks:
            return False

        landmarks = results.pose_landmarks.landmark

        upper_body_visible = any(landmarks[lm.value].visibility > VISIBILITY_THRESHOLD
                                 for lm in UPPER_BODY_LANDMARKS if lm.value < len(landmarks))
        lower_body_visible = any(landmarks[lm.value].visibility > VISIBILITY_THRESHOLD
                                 for lm in LOWER_BODY_LANDMARKS if lm.value < len(landmarks))

        return upper_body_visible and lower_body_visible

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e}")
        return False
    except cv2.error as e:
         print(f"OpenCV error processing {image_url}: {e}")
         return False
    except Exception as e:
        print(f"An unexpected error occurred processing {image_url}: {e}")
        return False

try:
    df = pd.read_csv(INPUT_CSV_PATH)
    print(f"Loaded {len(df)} rows from {INPUT_CSV_PATH}")
except FileNotFoundError:
    print(f"Error: Input file not found at {INPUT_CSV_PATH}")
    exit()
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit()

df['new_model_image_url'] = df['model_image_url']

total_rows = len(df)
for index, row in df.iterrows():
    print(f"\nProcessing Product {index + 1}/{total_rows}: {row.get('product_id', 'N/A')}")

    candidate_urls = []
    if pd.notna(row['model_image_url']) and isinstance(row['model_image_url'], str):
        candidate_urls.append(row['model_image_url'])

    if pd.notna(row['additional_images']) and isinstance(row['additional_images'], str):
        add_urls = row['additional_images'].replace(';',',').split(',')
        candidate_urls.extend([url.strip() for url in add_urls if url.strip()])

    unique_candidate_urls = list(dict.fromkeys(candidate_urls))

    print(f"Found {len(unique_candidate_urls)} unique candidate URLs.")

    found_full_body_url = None
    for img_url in unique_candidate_urls:
        print(f"Checking: {img_url}")
        if is_full_body_image(img_url):
            print(f"--> Found full body image: {img_url}")
            found_full_body_url = img_url
            break

    if found_full_body_url:
        df.loc[index, 'new_model_image_url'] = found_full_body_url
    else:
        print(f"No suitable full-body image found for product {row.get('product_id', 'N/A')}. Keeping original.")

pose_detector.close()

try:
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\nProcessing complete. Updated data saved to {OUTPUT_CSV_PATH}")
except Exception as e:
    print(f"Error saving CSV: {e}")

