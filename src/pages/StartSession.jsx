import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { startSession } from "../api/kycApi";

export default function StartSession() {
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleStart(e) {
    e.preventDefault();
    setError("");

    try {
      const res = await startSession({
        phone,
        email,
        full_name: fullName,
      });

      const sessionId = res.data.session.session_id;
      localStorage.setItem("session_id", sessionId);

      // ✅ APPLYING YOUR NAVIGATION
      navigate("/upload-pan");  // go straight to PAN upload
    } catch (err) {
      console.error(err);
      setError("Failed to start KYC. Check backend is running.");
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Start KYC Session</h2>
      <form onSubmit={handleStart}>
        <div>
          <input
            placeholder="Phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>
        <div>
          <input
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <input
            placeholder="Full Name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
        </div>
        <button type="submit">Start KYC</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
