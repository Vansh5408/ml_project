from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# ---------- Config ----------
FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3")

# ---------- App ----------
app = FastAPI(title="CineMate API")

# ---------- CORS Middleware ----------
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

# ---------- Paths / Artifacts ----------
MODEL_PATH = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
INDEX_PATH = os.environ.get("INDEX_PATH", "movie_index.faiss")
CSV_PATH = os.environ.get("CSV_PATH", "processed_movies.csv")

# ---------- Load artifacts ----------
print("🎬 Loading models and data...")

embed_model = SentenceTransformer(MODEL_PATH)
index = faiss.read_index(INDEX_PATH)
df = pd.read_csv(CSV_PATH)

# Clean NaN or inf data immediately
df.replace([np.inf, -np.inf, np.nan], "", inplace=True)

for col in ("title", "poster_url", "movie_link"):
    if col not in df.columns:
        df[col] = ""

llm = Ollama(model=MODEL_NAME)

prompt_template = """
You are CineMate, a friendly AI movie recommender.
A user has asked: "{query}"

Based on the following retrieved movies and their descriptions, 
recommend ONLY ONE movie and explain briefly why it fits.

Movies:
{retrieved_context}

Your final recommendation:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["query", "retrieved_context"])
chain = LLMChain(llm=llm, prompt=prompt)

print("✅ Backend ready!")

# ---------- Helper ----------
def retrieve_movies(query: str, model, index, df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    query_vector = model.encode([query]).astype("float32")
    if query_vector.ndim == 1:
        query_vector = np.expand_dims(query_vector, 0)
    distances, indices = index.search(query_vector, k)
    indices = indices[0]
    valid_indices = [int(i) for i in indices if 0 <= i < len(df)]
    retrieved = df.iloc[valid_indices].copy()
    retrieved.replace([np.inf, -np.inf, np.nan], "", inplace=True)
    return retrieved

# ---------- API: Recommend ----------
@app.post("/recommend")
def recommend_movie(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must be non-empty.")
    
    retrieved_docs = retrieve_movies(req.query, embed_model, index, df, k=req.k)

    retrieved_context = "\n\n".join([
        f"Title: {row.get('title','Unknown')}\nDescription: {row.get('description','')}"
        for _, row in retrieved_docs.iterrows()
    ])

    try:
        response_text = chain.run({"query": req.query, "retrieved_context": retrieved_context})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    # Clean float/NaN before returning
    clean_movies = (
        retrieved_docs[["title", "poster_url", "movie_link"]]
        .replace([np.inf, -np.inf, np.nan], "")
        .fillna("")
        .to_dict(orient="records")
    )

    return {
        "recommendation": response_text,
        "movies": clean_movies
    }

# ---------- API: Random ----------
@app.get("/random")
def get_random_movies(n: int = 8):
    if len(df) == 0:
        raise HTTPException(status_code=500, detail="Movie dataset is empty.")

    sampled_df = df.sample(n=min(n, len(df))).copy()
    sampled_df.replace([np.inf, -np.inf, np.nan], "", inplace=True)

    movies = (
        sampled_df[["title", "poster_url", "movie_link"]]
        .fillna("")
        .to_dict(orient="records")
    )
    return {"movies": movies}