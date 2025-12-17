// src/pages/UploadAadhaar.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../api/kycApi";

export default function UploadAadhaar() {
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
      setError("Please select an Aadhaar document file.");
      return;
    }

    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("doc_type", "AADHAAR");       // 🔴 Hard-coded Aadhaar
    formData.append("id_number", idNumber);
    formData.append("file", file);

    try {
      const res = await uploadDocument(formData);

      if (res.detail || res.error) {
        setError(JSON.stringify(res));
        return;
      }

      // After Aadhaar → go to photo upload
      navigate("/upload-photo");
    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.detail ||
        JSON.stringify(err.response?.data || "Unknown error");
      setError(`Failed to upload Aadhaar: ${msg}`);
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Aadhaar Document</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            placeholder="Aadhaar Number (12 digits)"
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
        <button type="submit">Upload Aadhaar</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
