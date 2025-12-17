import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css"; // ✅ IMPORTANT: this applies your global CSS

import StartSession from "./pages/StartSession";
import SelectDocument from "./pages/SelectDocument";
import UploadDocument from "./pages/UploadDocument";
import UploadPhoto from "./pages/UploadPhoto";
import UploadSelfie from "./pages/UploadSelfie";
import Completed from "./pages/Completed";

import UploadPAN from "./pages/UploadPAN";
import UploadAadhaar from "./pages/UploadAadhaar";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StartSession />} />
        <Route path="/select-document" element={<SelectDocument />} />
        <Route path="/upload-document" element={<UploadDocument />} />
        <Route path="/upload-photo" element={<UploadPhoto />} />
        <Route path="/upload-selfie" element={<UploadSelfie />} />
        <Route path="/completed" element={<Completed />} />

        <Route path="/upload-pan" element={<UploadPAN />} />
        <Route path="/upload-aadhaar" element={<UploadAadhaar />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
