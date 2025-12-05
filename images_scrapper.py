import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

# Function to clean the query (remove special characters)
def clean_query(text):
    # Keep only letters, numbers, and spaces
    return re.sub(r'[^a-zA-Z0-9 ]+', '', text)

# Load the original songs
with open('songs.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Setup Selenium headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)

output = []

for i, song in enumerate(songs):
    raw_title = song['song']
    raw_artist = song['artist']

    # Clean query to remove special characters
    title = clean_query(raw_title)
    artist = clean_query(raw_artist)

    query = quote(f"{title} {artist}")
    url = f"https://open.spotify.com/search/{query}"

    image_url = None
    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(f"🎵 Searching: '{title}' by '{artist}' (Attempt {attempt + 1})")
            driver.get(url)
            
            # Wait for card images to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="card-image"]'))
            )
            time.sleep(2)

            # Grab the first image shown
            image = driver.find_element(By.CSS_SELECTOR, '[data-testid="card-image"]')
            image_url = image.get_attribute('src')

            if image_url:
                print(f"✅ Image found: {image_url}")
                break
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print(f"⚠️ Failed after {max_retries} attempts for: {raw_title} by {raw_artist}")

    song['image_url'] = image_url
    output.append(song)

    print(f"{i+1}/{len(songs)} Processed: {raw_title}")

# Save the updated JSON
with open('songs_with_images.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

driver.quit()
