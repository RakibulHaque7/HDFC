import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadPhoto } from "../api/kycApi";

export default function UploadPhoto() {
  const [photo, setPhoto] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      setError("No session. Start KYC again.");
      return;
    }
    if (!photo) {
      setError("Please choose a passport-size photo.");
      return;
    }

    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("photo", photo);

    try {
      await uploadPhoto(formData);
      navigate("/upload-selfie");
    } catch (err) {
      console.error(err);
      setError("Failed to upload photo.");
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Passport-size Photo</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          onChange={(e) => setPhoto(e.target.files[0])}
        />
        <br />
        <button type="submit">Upload Photo</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
