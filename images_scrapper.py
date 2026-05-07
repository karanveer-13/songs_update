import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

def clean_query(text):
    return re.sub(r'[^a-zA-Z0-9 ]+', '', text)

def create_driver():
    """Initializes a fresh Chrome driver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Adding a window size can sometimes help with element visibility
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

# Load the original songs
with open('songs.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

output = []
driver = create_driver()
RESTART_EVERY = 40  # Restart browser every 40 songs to prevent crashes

try:
    for i, song in enumerate(songs):
        # Check if we need to restart the driver to clear memory
        if i > 0 and i % RESTART_EVERY == 0:
            print(f"🔄 Restarting browser to maintain performance...")
            driver.quit()
            driver = create_driver()

        raw_title = song['song']
        raw_artist = song['artist']
        title = clean_query(raw_title)
        artist = clean_query(raw_artist)

        query = quote(f"{title} {artist}")
        url = f"https://open.spotify.com/search/{query}"

        image_url = None
        max_retries = 3

        for attempt in range(max_retries):
            try:
                print(f"🎵 [{i+1}/200] Searching: '{title}' by '{artist}' (Attempt {attempt + 1})")
                driver.get(url)
                
                # Wait for card images to load
                wait = WebDriverWait(driver, 12)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="card-image"]')))
                
                # Small buffer for the src attribute to populate
                time.sleep(1.5)

                image = driver.find_element(By.CSS_SELECTOR, '[data-testid="card-image"]')
                image_url = image.get_attribute('src')

                if image_url:
                    print(f"  ✅ Found: {image_url[:50]}...")
                    break
            except Exception as e:
                print(f"  ❌ Attempt {attempt + 1} failed: {str(e)[:100]}")
                # If the tab crashed, we MUST restart the driver immediately
                if "tab crashed" in str(e).lower() or "session deleted" in str(e).lower():
                    driver.quit()
                    driver = create_driver()
                if attempt < max_retries - 1:
                    time.sleep(2)

        song['image_url'] = image_url
        output.append(song)

finally:
    # Save the updated JSON even if the script crashes halfway
    with open('songs_with_images.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    driver.quit()

print("✨ Finished processing all songs.")
