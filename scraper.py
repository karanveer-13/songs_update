import requests
from bs4 import BeautifulSoup
import json

URL = "https://kworb.net/spotify/country/global_weekly_totals.html"

# Add headers and explicitly handle encoding
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(URL, headers=headers)
response.encoding = 'utf-8'  # Force UTF-8 encoding

soup = BeautifulSoup(response.text, 'html.parser')
songs = []
rows = soup.select('table tbody tr')

for i, row in enumerate(rows[:200]):
    cols = row.find_all('td')
    if len(cols) < 7:
        continue
    
    artist_title_div = cols[0].find('div')
    if not artist_title_div:
        continue
    
    links = artist_title_div.find_all('a')
    if len(links) < 2:
        continue
    
    artist = links[0].text.strip()
    song = links[1].text.strip()
    
    try:
        wks = int(cols[1].text.strip())
    except ValueError:
        wks = None
    
    songs.append({
        "artist": artist,
        "song": song,
        "weeks_in_top_200": wks
    })

# Save to JSON file
with open("songs.json", "w", encoding="utf-8") as f:
    json.dump(songs, f, ensure_ascii=False, indent=2)

print(f"✅ Scraped and saved {len(songs)} songs to songs.json")
