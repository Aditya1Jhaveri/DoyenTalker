// LoadingScreen.js
import React, { useEffect, useState } from "react";
import "./LoadingScreen.css";

const LoadingScreen = () => {
  const [showLoading, setShowLoading] = useState(true);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setShowLoading(false);
    }, 60000);

    return () => clearTimeout(timeout); // Cleanup the timeout on unmount
  }, []);

  return (
    <div className={`loading-screen ${showLoading ? "visible" : "hidden"}`}>
      <div className="loader"></div>
      <div className="loading-text">Please wait...</div>
    </div>
  );
};

export default LoadingScreen;
