import requests
from bs4 import BeautifulSoup
import json

URL = "https://kworb.net/spotify/country/global_weekly_totals.html"
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

songs = []
rows = soup.select('table tbody tr')  # Select all rows inside the table

for i, row in enumerate(rows[:200]):  # Limit to first 200
    cols = row.find_all('td')
    if len(cols) < 7:
        continue  # skip malformed rows
    
    # Parse artist and song from the first <td>
    artist_title_div = cols[0].find('div')
    if not artist_title_div:
        continue
    
    links = artist_title_div.find_all('a')
    if len(links) < 2:
        continue  # skip if either artist or title is missing
    
    artist = links[0].text.strip()
    song = links[1].text.strip()
    
    # Parse weeks in top 200
    try:
        wks = int(cols[1].text.strip())
    except ValueError:
        wks = None  # fallback if parsing fails
    
    songs.append({
        "artist": artist,
        "song": song,
        "weeks_in_top_200": wks
    })

# Save to JSON file
with open("songs.json", "w", encoding="utf-8") as f:
    json.dump(songs, f, ensure_ascii=False, indent=2)

print(f"✅ Scraped and saved {len(songs)} songs to songs.json")
