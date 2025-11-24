import os
import sys
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# Load .env from current directory
print("🔍 Current working directory:", os.getcwd())
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Debug: show what dotenv found
print("🔎 OMDB_API_KEY (from .env):", os.environ.get("OMDB_API_KEY"))

OMDB_API_KEY = os.environ.get("OMDB_API_KEY")
if not OMDB_API_KEY:
    raise RuntimeError("❌ Please set OMDB_API_KEY in your environment variables.")


if len(sys.argv) < 2:
    print("Usage: python fetch_posters.py processed_movies.csv")
    sys.exit(1)

csv_path = sys.argv[1]
df = pd.read_csv(csv_path)

# Ensure columns exist
if "poster_url" not in df.columns:
    df["poster_url"] = ""
if "movie_link" not in df.columns:
    df["movie_link"] = ""

def fetch_omdb_data(title):
    """Fetch poster and link using OMDb API."""
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("Response") == "True":
                poster = data.get("Poster", "")
                imdb_id = data.get("imdbID", "")
                imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
                return poster, imdb_link
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return "", ""

print(f"🎬 Starting poster fetch for {len(df)} movies using OMDb API...")

for idx, row in df.iterrows():
    if pd.notna(row.get("poster_url")) and str(row.get("poster_url")).strip():
        continue  # skip if already has poster
    title = str(row.get("title", "")).strip()
    if not title:
        continue
    poster, link = fetch_omdb_data(title)
    df.at[idx, "poster_url"] = poster
    df.at[idx, "movie_link"] = link
    if idx % 10 == 0:
        print(f"Processed {idx+1}/{len(df)}...")
    time.sleep(0.25)  # be polite to API (4 calls/sec)

df.to_csv(csv_path, index=False)
print("✅ Poster enrichment complete! Updated file saved:", csv_path)