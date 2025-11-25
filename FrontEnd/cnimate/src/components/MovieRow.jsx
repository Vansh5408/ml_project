import React, { useEffect, useState } from "react";
import axios from "axios";
import "./MovieRow.css";

const MovieRow = () => {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8001";
        const res = await axios.get(`${base}/random?n=10`);
        setMovies(res.data.movies);
      } catch (error) {
        console.error("Error fetching movies:", error);
      }
    };
    fetchMovies();
  }, []);

  return (
    <div className="movie-row-container">
      <h2 className="row-title">Popular on CineMate 🍿</h2>
      <div className="movie-row">
        {movies.map((m, idx) => (
          <a key={idx} href={m.movie_link} target="_blank" rel="noreferrer" className="movie-card">
            <img src={m.poster_url} alt={m.title} />
            <div className="movie-hover">
              <p>{m.title}</p>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};

export default MovieRow;