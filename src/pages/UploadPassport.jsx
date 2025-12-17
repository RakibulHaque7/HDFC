import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function UploadPassport() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  // ✅ Get session from localStorage (set earlier in StartSession)
  const sessionId = localStorage.getItem("kyc_session_id");

  useEffect(() => {
    if (!sessionId) {
      // No active session → send user back to start
      navigate("/");
    }
  }, [sessionId, navigate]);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;

    // Optional: accept only images / pdfs
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
      setPreview(""); // no preview for pdf
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a passport image or scan first.");
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
      formData.append("doc_type", "PASSPORT"); // 👈 must match your Django DOC_TYPES
      formData.append("file", file);

      const res = await fetch("/api/kyc/upload-document/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        console.error(data);
        setError(data.detail || data.error || "Failed to upload passport.");
        return;
      }

      // Success 🎉 → go to UploadPhoto step
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
      <h1>Upload Passport</h1>
      <p>Please upload a clear image or scan of your Passport.</p>

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
              alt="Passport preview"
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
