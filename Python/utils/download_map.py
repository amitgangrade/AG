import requests
import os

url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/India_map_en.svg/856px-India_map_en.svg.png"
# Alternative high contrast: https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/India_location_map.svg/862px-India_location_map.svg.png
# Let's use the location map which is cleaner for plotting
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/India_location_map.svg/862px-India_location_map.svg.png"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    with open("india_map.png", "wb") as f:
        f.write(response.content)
    print("Map downloaded successfully.")
else:
    print("Failed to download map.")
