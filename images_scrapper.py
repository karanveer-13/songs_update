import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import quote

# Load the original songs
with open('songs.json', 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Setup Selenium headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

output = []

for i, song in enumerate(songs):
    title = song['song']
    artist = song['artist']
    query = quote(f"{title} {artist}")
    url = f"https://open.spotify.com/search/{query}"

    driver.get(url)
    time.sleep(3)  # let the JS render

    try:
        # Get the first result image
        image = driver.find_element(By.CSS_SELECTOR, '[data-testid="card-image"]')
        image_url = image.get_attribute('src')
    except Exception:
        print(f"⚠️ Image not found for: {title} by {artist}")
        image_url = None

    song['image_url'] = image_url
    output.append(song)

    print(f"{i+1}/{len(songs)} done: {title}")

# Save the new JSON
with open('songs_with_images.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

driver.quit()
