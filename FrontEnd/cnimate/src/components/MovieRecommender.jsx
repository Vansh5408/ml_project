// src/components/MovieRecommender.jsx
import React, { useState } from "react";
import axios from "axios";
import "./MovieRecommender.css";

const MovieRecommender = () => {
  const [query, setQuery] = useState("");
  const [recommendation, setRecommendation] = useState("");
  const [movies, setMovies] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setRecommendation("Loading...");
    setMovies([]);

    try {
      const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8001";
      const res = await axios.post(`${base}/recommend`, { query });
      setRecommendation(res.data.recommendation);
      setMovies(res.data.movies || []);
    } catch (err) {
      console.error(err);
      // show backend error message when available for easier debugging
      const backendMsg = err?.response?.data || err?.message || "Error fetching recommendation.";
      setRecommendation(typeof backendMsg === "string" ? backendMsg : JSON.stringify(backendMsg));
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="navbar">
        <h1 className="logo">🎬 CineMate</h1>
        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search or describe your mood..."
            className="search-input"
          />
          <button type="submit" className="search-btn">
            Recommend
          </button>
        </form>
      </header>

      {/* Recommendation Output */}
      {recommendation && (
        <div className="recommendation-box">
          <h2 className="section-title">AI Suggestion 💡</h2>
          <p>{recommendation}</p>
        </div>
      )}

      {/* Movie Grid */}
      {movies.length > 0 && (
        <div className="movie-section">
          <h2 className="section-title">Related Movies 🍿</h2>
          <div className="movie-grid">
            {movies.map((m, idx) => (
              <div key={idx} className="movie-card">
                {m.poster_url ? (
                  <img src={m.poster_url} alt={m.title} className="movie-poster" />
                ) : (
                  <div className="poster-placeholder">🎥</div>
                )}
                <h3>{m.title}</h3>
                {m.movie_link && (
                  <a
                    href={m.movie_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-link"
                  >
                    View More →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MovieRecommender;