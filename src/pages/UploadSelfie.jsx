import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadSelfie } from "../api/kycApi";

export default function UploadSelfie() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();

  // Start the camera when component mounts
  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" }, // front camera on mobile
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Camera error:", err);
        setError(
          "Could not access camera. Please allow camera permissions or use a device with a camera."
        );
      }
    }

    startCamera();

    // Clean up: stop camera on unmount
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  async function handleCapture() {
    setError("");

    const sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      setError("No KYC session found. Please start again.");
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) {
      setError("Camera not ready.");
      return;
    }

    // Draw current video frame to canvas
    const width = video.videoWidth || 300;
    const height = video.videoHeight || 300;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, width, height);

    // Convert canvas to image blob and upload
    setIsUploading(true);
    canvas.toBlob(async (blob) => {
      if (!blob) {
        setError("Failed to capture image from camera.");
        setIsUploading(false);
        return;
      }

      const formData = new FormData();
      formData.append("session_id", sessionId);
      formData.append("live_selfie", blob, "selfie.jpg");

      try {
        const res = await uploadSelfie(formData);
        console.log("Selfie upload response:", res.data);
        navigate("/completed");
      } catch (err) {
        console.error("Upload selfie error:", err);
        // Show real backend message if available
        const detail =
          err.response?.data?.detail ||
          JSON.stringify(err.response?.data || "Unknown error");
        setError(`Failed to upload selfie: ${detail}`);
      } finally {
        setIsUploading(false);
      }
    }, "image/jpeg");
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Live Selfie</h2>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{ width: "300px", borderRadius: "8px", border: "1px solid #ccc" }}
      />
      <br />
      <button onClick={handleCapture} disabled={isUploading}>
        {isUploading ? "Uploading..." : "Capture & Finish KYC"}
      </button>

      {/* Hidden canvas just for capturing frame */}
      <canvas ref={canvasRef} style={{ display: "none" }} />

      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}
    </div>
  );
}
