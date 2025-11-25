import React, { useEffect, useState } from "react";
import axios from "axios";
import "./HeroBanner.css";

const HeroBanner = () => {
  const [featuredMovie, setFeaturedMovie] = useState(null);

  useEffect(() => {
    const fetchRandomMovie = async () => {
      try {
        const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8001";
        const res = await axios.get(`${base}/random?n=1`);
        setFeaturedMovie(res.data.movies[0]);
      } catch (error) {
        console.error("Error fetching featured movie:", error);
      }
    };
    fetchRandomMovie();
  }, []);

  if (!featuredMovie) return <div className="hero-loading">Loading...</div>;

  return (
    <div
      className="hero-banner"
      style={{
        backgroundImage: `url(${featuredMovie.poster_url})`,
      }}
    >
      <div className="hero-overlay">
        <div className="hero-content">
          <h1 className="hero-title">{featuredMovie.title}</h1>
          <div className="hero-buttons">
            <a href={featuredMovie.movie_link} target="_blank" rel="noreferrer" className="hero-btn play-btn">
              ▶ Watch Now
            </a>
            <button className="hero-btn info-btn">More Info</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroBanner;