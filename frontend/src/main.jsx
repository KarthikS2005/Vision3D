// src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

// Load model-viewer
const script = document.createElement("script");
script.type = "module";
script.src = "https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js";
document.head.appendChild(script);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);