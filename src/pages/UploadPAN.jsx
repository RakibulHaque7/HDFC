// src/pages/UploadPAN.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../api/kycApi";

export default function UploadPAN() {
  const [idNumber, setIdNumber] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      setError("No session. Please start KYC again.");
      return;
    }
    if (!file) {
      setError("Please select a PAN document file.");
      return;
    }

    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("doc_type", "PAN");           // 🔴 Hard-coded PAN
    formData.append("id_number", idNumber);
    formData.append("file", file);

    try {
      const res = await uploadDocument(formData);

      // Backend may return errors as JSON, show if present
      if (res.detail || res.error) {
        setError(JSON.stringify(res));
        return;
      }

      // After PAN → go to Aadhaar upload
      navigate("/upload-aadhaar");
    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.detail ||
        JSON.stringify(err.response?.data || "Unknown error");
      setError(`Failed to upload PAN: ${msg}`);
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload PAN Document</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            placeholder="PAN Number (ABCDE1234F)"
            value={idNumber}
            onChange={(e) => setIdNumber(e.target.value)}
          />
        </div>
        <div>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
        <button type="submit">Upload PAN</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
