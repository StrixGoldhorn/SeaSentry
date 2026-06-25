import { Routes, Route } from "react-router";
import MapPage from "./MapPage";
import { RequestInputPage } from "./RequestInputPage";
import DrawAOIPage from "./DrawAOIPage";
import DrawGeofencePage from "./DrawGeofencePage";
import SidebarAOIDrawPage from "./SidebarAOIDraw";
import SidebarGeofenceDrawPage from "./SidebarGeofenceDraw";
import AlertHistoryPage from "./AlertHistoryPage";


function App() {
  return (
    <Routes>
      <Route path="/" element={<MapPage />} />
      <Route path="/drawAOI" element={<DrawAOIPage />} />
      <Route path="/drawGeofence" element={<DrawGeofencePage />} />
      <Route path="/drawAOIsidebar" element={<SidebarAOIDrawPage />} />
      <Route path="/drawGeofenceSidebar" element={<SidebarGeofenceDrawPage />} />
      <Route path="/inputs" element={<RequestInputPage />} />
      <Route path="/alerts/history" element={<AlertHistoryPage/>} />
    </Routes>
  );
}

export default App;