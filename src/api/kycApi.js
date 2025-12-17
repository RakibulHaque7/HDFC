// src/api/kycApi.js
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000", // your Django backend
});

// 1) Start session
export const startSession = (data) =>
  API.post("/api/kyc/start-session/", data);

// 2) Select document
export const selectDocument = (data) =>
  API.post("/api/kyc/select-document/", data);

// 3) Upload document
export const uploadDocument = (formData) =>
  API.post("/api/kyc/upload-document/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// 4) Upload passport-size photo
export const uploadPhoto = (formData) =>
  API.post("/api/kyc/upload-photo/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// 5) Upload live selfie
export const uploadSelfie = (formData) =>
  API.post("/api/kyc/upload-live-selfie/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
