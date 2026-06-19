import { useState, useRef } from "react";
import "./App.css";





function App() {
  const [started, setStarted] = useState(false);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const cameraRef = useRef(null);
  const galleryRef = useRef(null);
  const fileRef = useRef(null);



 const handleSubmit = async () => {
  if (!file) {
    alert("Please select an image");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Prediction failed");
    }

    setResult(data);
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
};

  if (!started) {
    return (
      <div className="landing">
        <h1 className="main-title">Potato Disease Detection</h1>
        <h2>AI Powered Crop Health Analysis</h2>
        <button className="start-btn" onClick={() => setStarted(true)}>
          Get Started
        </button>
      </div>
    );
  }

  return (
    <div className="predict-page">
      <input
        ref={cameraRef}
        type="file"
        accept="image/*"
        capture="environment"
        style={{ display: "none" }}
        onChange={(e) => setFile(e.target.files[0])}
      />
      <input
        ref={galleryRef}
        type="file"
        accept="image/*"
        style={{ display: "none" }}
        onChange={(e) => setFile(e.target.files[0])}
      />
      <input
        ref={fileRef}
        type="file"
        style={{ display: "none" }}
        onChange={(e) => setFile(e.target.files[0])}
      />

      <div className="predict-card">
        <h1 className="main-title predict-title">Potato Disease Detector</h1>

        <div className="buttons">
          <button onClick={() => cameraRef.current.click()}>📷 Take Photo</button>
          <button onClick={() => galleryRef.current.click()}>🖼️ Gallery</button>
          <button onClick={() => fileRef.current.click()}>📁 Upload File</button>
        </div>

        {file && (
          <img
            src={URL.createObjectURL(file)}
            alt="preview"
            className="preview"
          />
        )}

        <button className="predict-btn" onClick={handleSubmit}>
          Predict
        </button>

        {result && (
          <div className="result">
            <h2>{result.class}</h2>
            <h3>Confidence: {(result.confidence * 100).toFixed(2)}%</h3>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;