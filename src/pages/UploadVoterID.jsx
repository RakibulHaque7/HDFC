import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function UploadVoterID() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  const sessionId = localStorage.getItem("kyc_session_id");

  useEffect(() => {
    if (!sessionId) {
      navigate("/");
    }
  }, [sessionId, navigate]);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;

    if (!selected.type.startsWith("image/") && selected.type !== "application/pdf") {
      setError("Please upload an image or PDF file.");
      setFile(null);
      setPreview("");
      return;
    }

    setError("");
    setFile(selected);

    if (selected.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(selected);
    } else {
      setPreview("");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError("Please select your Voter ID image or scan first.");
      return;
    }

    if (!sessionId) {
      setError("No active KYC session found. Please start again.");
      return;
    }

    try {
      setIsUploading(true);
      setError("");

      const formData = new FormData();
      formData.append("session_id", sessionId);
      formData.append("doc_type", "VOTER_ID"); // 👈 must match Django DOC_TYPES choice
      formData.append("file", file);

      const res = await fetch("/api/kyc/upload-document/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        console.error(data);
        setError(data.detail || data.error || "Failed to upload Voter ID.");
        return;
      }

      navigate("/upload-photo");
    } catch (err) {
      console.error(err);
      setError("Something went wrong while uploading. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="page">
      <h1>Upload Voter ID</h1>
      <p>Please upload a clear image or scan of your Voter ID card.</p>

      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Select file:
            <input
              type="file"
              accept="image/*,application/pdf"
              onChange={handleFileChange}
              disabled={isUploading}
            />
          </label>
        </div>

        {preview && (
          <div style={{ marginTop: "1rem" }}>
            <p>Preview:</p>
            <img
              src={preview}
              alt="Voter ID preview"
              style={{ maxWidth: "300px", borderRadius: "8px" }}
            />
          </div>
        )}

        {error && (
          <p style={{ color: "red", marginTop: "0.75rem" }}>
            {error}
          </p>
        )}

        <button type="submit" disabled={isUploading} style={{ marginTop: "1rem" }}>
          {isUploading ? "Uploading..." : "Upload & Continue"}
        </button>
      </form>
    </div>
  );
}


