import React from "react";
import HeroBanner from "./components/HeroBanner";
import MovieRow from "./components/MovieRow";
import MovieRecommender from "./components/MovieRecommender";

const App = () => {
  return (
    <div style={{ backgroundColor: "#0f0f0f", minHeight: "100vh", color: "#fff" }}>
      <HeroBanner />
      <MovieRow />
      <MovieRecommender />
    </div>
  );
};

export default App;