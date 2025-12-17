import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../api/kycApi";

export default function UploadDocument() {
  const [idNumber, setIdNumber] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const sessionId = localStorage.getItem("session_id");
    const docType = localStorage.getItem("doc_type");

    if (!sessionId || !docType) {
      setError("Missing session or document type. Start again.");
      return;
    }
    if (!file) {
      setError("Please select a document file.");
      return;
    }

    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("doc_type", docType);
    formData.append("id_number", idNumber);
    formData.append("file", file);

    try {
      const res = await uploadDocument(formData);

      if (res.detail || res.error) {
        setError(JSON.stringify(res));
        return;
      }

      navigate("/upload-photo");
    } catch (err) {
      console.error(err);
      setError("Failed to upload document.");
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Document</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            placeholder="Document Number (PAN/Aadhaar)"
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
        <button type="submit">Upload</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
