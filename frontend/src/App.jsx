import { useState } from "react";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [modelUrl, setModelUrl] = useState("");
  const [error, setError] = useState("");

  const generate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError("");
    setModelUrl("");

    try {
      const response = await fetch("http://127.0.0.1:8000/generate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",           // ← JSON!
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ prompt: prompt.trim() }), // ← JSON body
      });

      const data = await response.json();

      if (data.success) {
        setModelUrl(`http://127.0.0.1:8000${data.model_url}?t=${Date.now()}`);
        setError("Success! Drag to rotate");
      } else {
        setError("Error from server");
        setModelUrl("http://127.0.0.1:8000/generated/fallback.glb");
      }
    } catch (err) {
      setError("Cannot connect to Django backend. Is it running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-5xl font-bold text-center mb-10 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
          3D models give simple prompt it i'll generate 3d mesh model 
        </h1>

        <div className="flex gap-4 mb-8">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && generate()}
            placeholder="a low poly dragon, a robot, a crystal castle..."
            className="flex-1 p-5 rounded-xl bg-gray-800 text-xl outline-none focus:ring-4 focus:ring-purple-600 transition"
          />
          <button
            onClick={generate}
            disabled={loading}
            className="px-12 py-5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 rounded-xl font-bold text-xl shadow-lg transition"
          >
            {loading ? "Generating..." : "Generate 3D"}
          </button>
        </div>

        {error && (
          <div className="text-center text-lg mb-6 p-4 bg-gray-800 rounded-lg">
            {error}
          </div>
        )}

        {/* Google Model Viewer */}
        {modelUrl && (
          <model-viewer
            src={modelUrl}
            alt="Generated 3D Model"
            camera-controls
            auto-rotate
            ar
            shadow-intensity="2"
            exposure="1.2"
            style={{
              width: "100%",
              height: "640px",
              background: "linear-gradient(135deg, #1a1a2e, #16213e)",
              borderRadius: "20px",
              boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
            }}
          ></model-viewer>
        )}

        {!modelUrl && !loading && (
          <div className="h-96 bg-gray-800 rounded-2xl flex items-center justify-center text-gray-500 text-2xl border-2 border-dashed border-gray-700">
            Your 3D model will appear here
          </div>
        )}
      </div>
    </div>
  );
}

export default App;