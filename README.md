# PAE - Personalized Apparel Engine

A skin-tone-aware fashion recommendation system that matches users with clothing products based on skin color similarity between the user and product models.

## Overview

PAE is an end-to-end machine learning pipeline that:
1. Scrapes fashion product data from e-commerce platforms
2. Analyzes model images to detect pose and orientation
3. Extracts skin color information from model images
4. Detects product gender categories
5. Recommends products to users based on skin tone similarity

The system uses computer vision techniques including pose estimation, skin segmentation, and color clustering to provide personalized fashion recommendations.

## Features

- **Web Scraping**: Automated product data collection from Myntra
- **Pose Detection**: MediaPipe-based pose analysis to identify front-facing full-body model images
- **Skin Color Detection**: HSV-based skin segmentation with KMeans clustering for dominant color extraction
- **Gender Classification**: Keyword frequency analysis for product gender categorization
- **Personalized Recommendations**: RGB color distance-based matching between user and product models

## Architecture

```
┌─────────────┐     ┌───────────────┐     ┌─────────────────────┐
│  scraper.py │────▶│ model_image.py│────▶│skin_color_detector.py│
└─────────────┘     └───────────────┘     └─────────────────────┘
                                                    │
                                                    ▼
                    ┌─────────────┐          ┌───────────┐
                    │   model.py  │◀─────────│ gender.py │
                    └─────────────┘          └───────────┘
                          │
                          ▼
                   [Recommendations]
```

## Project Structure

```
PAE/
├── scraper.py              # Myntra product scraper using Selenium
├── model_image.py          # Pose detection and model image selection
├── skin_color_detector.py  # Skin color extraction from model images
├── gender.py               # Gender detection from product pages
├── model.py                # Recommendation engine
├── data/                   # Dataset directory
│   ├── pae_dataset.csv
│   ├── final.csv
│   └── ...
├── LICENSE
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser (for web scraping)
- ChromeDriver (matching your Chrome version)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/PAE.git
   cd PAE
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download ChromeDriver** (for scraping)
   
   - Download from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Extract and update the path in `scraper.py`:
     ```python
     CHROMEDRIVER_PATH = r"C:\path\to\chromedriver.exe"
     ```

## Usage

### Step 1: Scrape Product Data

Collect product data from Myntra:

```bash
python scraper.py
```

This will:
- Search for products on Myntra
- Extract product details (title, price, description, images)
- Save data to `data/products.csv`
- Download product images to `data/images/`

**Note**: Modify `SEARCH_QUERY` in `scraper.py` to customize the product search.

### Step 2: Select Best Model Images

Analyze images to find front-facing model shots:

```bash
python model_image.py
```

This uses MediaPipe pose detection to:
- Identify full-body vs upper-body poses
- Detect front-facing orientation
- Select the best model image for each product

### Step 3: Extract Skin Colors

Detect dominant skin color from model images:

```bash
python skin_color_detector.py
```

Uses HSV color space segmentation and KMeans clustering to extract skin tone.

### Step 4: Detect Gender Categories

Classify products by gender:

```bash
python gender.py
```

Scrapes product pages and uses keyword frequency analysis to determine gender categories.

### Step 5: Get Recommendations

Run the recommendation engine:

```bash
python model.py
```

You will be prompted to:
1. Enter your gender (Men, Women, Boys, Girls)
2. Provide the path to your photo

The system will analyze your skin tone and recommend products with models having similar skin colors.

## Configuration

### Skin Detection Parameters

In `skin_color_detector.py` and `model.py`:

```python
LOWER_SKIN_HSV = np.array([0, 40, 50], dtype="uint8")   # HSV lower bound
UPPER_SKIN_HSV = np.array([25, 150, 255], dtype="uint8") # HSV upper bound
MIN_SKIN_PIXELS = 500  # Minimum pixels required for detection
```

### Pose Detection Parameters

In `model_image.py`:

```python
VISIBILITY_THRESHOLD = 0.65        # Landmark visibility threshold
MIN_VISIBLE_LANDMARKS_OVERALL = 8  # Minimum landmarks for valid pose
VERTICAL_SPREAD_THRESHOLD = 0.6    # Full-body detection threshold
```

## Data Pipeline

| Stage | Input | Output | Description |
|-------|-------|--------|-------------|
| Scraping | Search query | `products.csv` | Raw product data |
| Model Selection | `pae_dataset.csv` | `myntra_data_updated_front_facing.csv` | Best model images |
| Skin Detection | Front-facing images | `myntra_data_with_skin_color.csv` | RGB skin colors |
| Gender Detection | Product URLs | `myntra_data_with_gender_freq_v2.csv` | Gender categories |
| Recommendation | `final.csv` + User photo | Top N products | Personalized results |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >= 2.0.0 | Data manipulation |
| numpy | >= 1.24.0 | Numerical operations |
| opencv-python | >= 4.8.0 | Image processing |
| mediapipe | >= 0.10.0 | Pose detection |
| scikit-learn | >= 1.3.0 | KMeans clustering |
| selenium | >= 4.15.0 | Web scraping |
| requests | >= 2.31.0 | HTTP requests |
| beautifulsoup4 | >= 4.12.0 | HTML parsing |

## Limitations

- **Skin detection accuracy**: Works best with well-lit images and visible skin areas
- **Scraping constraints**: Subject to website structure changes and rate limiting
- **Gender detection**: Relies on keyword frequency; may not capture all nuances
- **ChromeDriver dependency**: Requires matching Chrome browser version

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for pose detection
- [OpenCV](https://opencv.org/) for image processing
- [scikit-learn](https://scikit-learn.org/) for machine learning utilities

