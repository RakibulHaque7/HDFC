import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { selectDocument } from "../api/kycApi";

const DOC_OPTIONS = [
  { value: "PAN", label: "PAN Card" },
  { value: "AADHAAR", label: "Aadhaar Card" },
  { value: "PASSPORT", label: "Passport" },
  { value: "VOTER", label: "Voter ID" },
];

export default function SelectDocument() {
  const [docType, setDocType] = useState("PAN");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      setError("No session_id found. Please start KYC again.");
      return;
    }

    try {
      await selectDocument({
        session_id: sessionId,
        doc_type: docType,
      });

      // save for UploadDocument step
      localStorage.setItem("doc_type", docType);

      navigate("/upload-document");
    } catch (err) {
      console.error(err);
      setError("Failed to select document type.");
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Select Document Type</h2>
      <form onSubmit={handleSubmit}>
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
        >
          {DOC_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <br />
        <button type="submit">Continue</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
