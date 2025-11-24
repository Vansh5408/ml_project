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
      const res = await axios.post("http://127.0.0.1:8000/recommend", { query });
      setRecommendation(res.data.recommendation);
      setMovies(res.data.movies || []);
    } catch (err) {
      console.error(err);
      setRecommendation("Error fetching recommendation.");
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