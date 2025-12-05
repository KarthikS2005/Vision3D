import { useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [modelUrl, setModelUrl] = useState("");
  const [error, setError] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [printParams, setPrintParams] = useState(null);
  const [layerHeight, setLayerHeight] = useState(0.2);
  const [infillDensity, setInfillDensity] = useState(20);

  const generate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError("");
    setModelUrl("");
    setMetrics(null);
    setPrintParams(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/generate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ 
          prompt: prompt.trim(),
          layer_height: layerHeight,
          infill_density: infillDensity
        }),
      });

      const data = await response.json();

      if (data.success) {
        setModelUrl(`http://127.0.0.1:8000${data.model_url}?t=${Date.now()}`);
        setMetrics({
          cached: data.cached,
          generationTime: data.generation_time,
          responseTime: data.response_time,
        });
        setPrintParams(data.print_parameters);
        setError("");
      } else {
        setError(data.error || "Error generating model");
      }
    } catch (err) {
      setError("Cannot connect to backend. Is the server running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Animated Background */}
      <div className="background-gradient"></div>
      <div className="background-overlay"></div>

      <div className="content-wrapper">
        {/* Header */}
        <header className="header">
          <div className="logo-container">
            <div className="logo-icon">🎨</div>
            <h1 className="logo-text">Vision3D Pro</h1>
          </div>
          <p className="tagline">Transform Text into 3D Printable Models</p>
        </header>

        {/* Input Section */}
        <div className="input-section">
          <div className="input-wrapper">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && generate()}
              placeholder="Describe your 3D model... (e.g., 'a red robot', 'blue car', 'gold pendant')"
              className="prompt-input"
              disabled={loading}
            />
            <button
              onClick={generate}
              disabled={loading || !prompt.trim()}
              className="generate-button"
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                <>
                  <span className="button-icon">✨</span>
                  Generate 3D
                </>
              )}
            </button>
          </div>

          {/* Print Settings */}
          <div className="print-settings">
            <div className="setting-group">
              <label>
                Layer Height: <strong>{layerHeight}mm</strong>
                <span className="setting-hint">(Resolution vs Speed)</span>
              </label>
              <input
                type="range"
                min="0.1"
                max="0.3"
                step="0.05"
                value={layerHeight}
                onChange={(e) => setLayerHeight(parseFloat(e.target.value))}
                className="slider"
              />
              <div className="slider-labels">
                <span>Fine (0.1mm)</span>
                <span>Fast (0.3mm)</span>
              </div>
            </div>

            <div className="setting-group">
              <label>
                Infill Density: <strong>{infillDensity}%</strong>
                <span className="setting-hint">(Strength vs Material)</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={infillDensity}
                onChange={(e) => setInfillDensity(parseInt(e.target.value))}
                className="slider"
              />
              <div className="slider-labels">
                <span>Light (0%)</span>
                <span>Solid (100%)</span>
              </div>
            </div>
          </div>

          {/* Quick Suggestions */}
          {!modelUrl && !loading && (
            <div className="suggestions">
              <span className="suggestions-label">Try:</span>
              {["a blue robot", "red car", "gold pendant", "green sphere"].map((suggestion) => (
                <button
                  key={suggestion}
                  className="suggestion-chip"
                  onClick={() => setPrompt(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Metrics Display */}
        {metrics && (
          <div className="metrics-panel">
            <div className="metric">
              <span className="metric-label">Status:</span>
              <span className={`metric-value ${metrics.cached ? 'cached' : 'generated'}`}>
                {metrics.cached ? '⚡ Cached' : '🎨 Generated'}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Generation Time:</span>
              <span className="metric-value">{metrics.generationTime.toFixed(2)}s</span>
            </div>
            <div className="metric">
              <span className="metric-label">Response Time:</span>
              <span className="metric-value">{metrics.responseTime.toFixed(3)}s</span>
            </div>
          </div>
        )}

        {/* Print Parameters Panel */}
        {printParams && (
          <div className="print-params-panel">
            <h3 className="params-title">📐 3D Printing Parameters</h3>
            
            <div className="params-grid">
              {/* Layer Settings */}
              <div className="param-card">
                <div className="param-icon">📏</div>
                <div className="param-content">
                  <h4>Layer Settings</h4>
                  <p><strong>Height:</strong> {printParams.layer_height_mm}mm</p>
                  <p><strong>Total Layers:</strong> {printParams.layer_count}</p>
                </div>
              </div>

              {/* Infill Settings */}
              <div className="param-card">
                <div className="param-icon">🔲</div>
                <div className="param-content">
                  <h4>Infill Configuration</h4>
                  <p><strong>Density:</strong> {printParams.infill_density_percent}%</p>
                  <p><strong>Pattern:</strong> {printParams.infill_pattern}</p>
                </div>
              </div>

              {/* Wall Settings */}
              <div className="param-card">
                <div className="param-icon">🧱</div>
                <div className="param-content">
                  <h4>Shell/Walls</h4>
                  <p><strong>Wall Count:</strong> {printParams.wall_count}</p>
                  <p><strong>Thickness:</strong> {printParams.wall_thickness_mm}mm</p>
                </div>
              </div>

              {/* Support Structures */}
              <div className="param-card">
                <div className="param-icon">🏗️</div>
                <div className="param-content">
                  <h4>Support Structures</h4>
                  <p><strong>Required:</strong> {printParams.supports_needed ? 'Yes' : 'No'}</p>
                  <p><strong>Type:</strong> {printParams.support_type}</p>
                </div>
              </div>

              {/* Orientation */}
              <div className="param-card">
                <div className="param-icon">🔄</div>
                <div className="param-content">
                  <h4>Orientation</h4>
                  <p>{printParams.orientation}</p>
                </div>
              </div>

              {/* Model Dimensions */}
              <div className="param-card">
                <div className="param-icon">📦</div>
                <div className="param-content">
                  <h4>Model Size</h4>
                  <p><strong>Volume:</strong> {printParams.model_volume_cm3} cm³</p>
                  <p><strong>Height:</strong> {printParams.model_height_mm}mm</p>
                </div>
              </div>
            </div>

            {/* Print Time & Cost Summary */}
            <div className="cost-summary">
              <div className="summary-item time">
                <div className="summary-icon">⏱️</div>
                <div className="summary-content">
                  <h4>Estimated Print Time</h4>
                  <p className="summary-value">{printParams.print_time_hours}h ({printParams.print_time_minutes} min)</p>
                </div>
              </div>

              <div className="summary-item cost">
                <div className="summary-icon">💰</div>
                <div className="summary-content">
                  <h4>Estimated Cost</h4>
                  <p className="summary-value">${printParams.material_cost_usd}</p>
                  <p className="summary-detail">{printParams.material_weight_g}g of material</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* 3D Model Viewer */}
        <div className="viewer-container">
          {modelUrl ? (
            <div className="model-viewer-wrapper">
              <model-viewer
                src={modelUrl}
                alt="Generated 3D Model"
                camera-controls
                auto-rotate
                ar
                shadow-intensity="2"
                exposure="1.2"
                className="model-viewer"
              ></model-viewer>
              <div className="viewer-controls-hint">
                <p>🖱️ Drag to rotate • Scroll to zoom • Right-click to pan</p>
              </div>
            </div>
          ) : loading ? (
            <div className="loading-placeholder">
              <div className="loading-spinner-large"></div>
              <p className="loading-text">Crafting your 3D masterpiece...</p>
            </div>
          ) : (
            <div className="empty-placeholder">
              <div className="placeholder-icon">🎭</div>
              <h3>Your 3D Model Will Appear Here</h3>
              <p>Enter a prompt above and click Generate to get started</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="footer">
          <p>Powered by Vision3D Pro • Advanced 3D Printing Optimization Engine</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
