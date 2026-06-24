import { Routes, Route } from "react-router";
import MapPage from "./MapPage";
import { RequestInputPage } from "./RequestInputPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<MapPage />} />
      <Route path="/inputs" element={<RequestInputPage />} />
    </Routes>
  );
}

export default App;