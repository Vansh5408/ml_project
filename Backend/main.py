from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Optional: heavy imports
HAS_FAISS = True
HAS_SENTENCE_TRANSFORMERS = True

try:
    import faiss
except Exception:
    HAS_FAISS = False

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    HAS_SENTENCE_TRANSFORMERS = False

import os
from dotenv import load_dotenv
import requests

# Load env vars
load_dotenv()

# ---------- Config ----------
FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").lower()

# ---------- App ----------
app = FastAPI(title="CineMate API")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request Schema ----------
class QueryRequest(BaseModel):
    query: str
    k: int = 5

# ---------- Paths ----------
MODEL_PATH = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
INDEX_PATH = os.environ.get("INDEX_PATH", "movie_index.faiss")
CSV_PATH = os.environ.get("CSV_PATH", "processed_movies.csv")

# ---------- Load dataset ----------
df = pd.read_csv(CSV_PATH)
df.replace([np.inf, -np.inf, np.nan], "", inplace=True)

for col in ("title", "poster_url", "movie_link", "description"):
    if col not in df.columns:
        df[col] = ""

embed_model = None
index = None

if HAS_SENTENCE_TRANSFORMERS and HAS_FAISS:
    try:
        embed_model = SentenceTransformer(MODEL_PATH)
    except Exception as e:
        print(f"Warning loading embed model: {e}")

    try:
        index = faiss.read_index(INDEX_PATH)
    except Exception as e:
        print(f"Warning loading faiss index: {e}")

prompt_template = """
You are CineMate, a friendly AI movie recommender.
A user has asked: "{query}"

Based on the following retrieved movies and their descriptions,
recommend ONLY ONE movie and explain briefly why it fits.

Movies:
{retrieved_context}

Your final recommendation:
"""

print("✅ Backend ready!")


# -------- Helper: Retrieve Movies --------
def retrieve_movies(query: str, model, index, df: pd.DataFrame, k: int = 5):
    if model is None or index is None:
        return df.sample(n=min(k, len(df))).copy()

    vec = model.encode([query]).astype("float32")
    distances, indices = index.search(vec, k)
    idx = [int(i) for i in indices[0] if 0 <= i < len(df)]
    return df.iloc[idx].copy()


# -------- Gemini API (Fully Fixed) --------
def gemini_generate(text_prompt: str) -> str:
    url = os.environ.get("GEMINI_API_URL")
    api_key = os.environ.get("GEMINI_API_KEY")

    if not url:
        raise RuntimeError("GEMINI_API_URL missing")

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key   # 🔥 Correct Gemini header
    }

    # 🔥 Correct request format for Gemini 2.5 Flash
    body = {
        "contents": [
            {
                "parts": [
                    {"text": text_prompt}
                ]
            }
        ]
    }

    resp = requests.post(url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Extract text safely
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return str(data)


# -------- API: Recommend --------
@app.post("/recommend")
def recommend(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query must be non-empty.")

    retrieved_docs = retrieve_movies(req.query, embed_model, index, df, req.k)

    retrieved_context = "\n\n".join([
        f"Title: {row['title']}\nDescription: {row.get('description','')}"
        for _, row in retrieved_docs.iterrows()
    ])

    combined_prompt = prompt_template.format(
        query=req.query,
        retrieved_context=retrieved_context
    )

    try:
        llm_output = gemini_generate(combined_prompt)
    except Exception as e:
        raise HTTPException(500, f"LLM call failed: {e}")

    clean_movies = (
        retrieved_docs[["title", "poster_url", "movie_link"]]
        .replace([np.inf, -np.inf, np.nan], "")
        .to_dict(orient="records")
    )

    return {
        "recommendation": llm_output,
        "movies": clean_movies
    }


# -------- API: Random --------
@app.get("/random")
def get_random_movies(n: int = 8):
    sample = df.sample(n=min(n, len(df))).copy()
    sample.replace([np.inf, -np.inf, np.nan], "", inplace=True)

    movies = (
        sample[["title", "poster_url", "movie_link"]]
        .to_dict(orient="records")
    )

    return {"movies": movies}
