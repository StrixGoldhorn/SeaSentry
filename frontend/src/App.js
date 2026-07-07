import { Routes, Route } from "react-router";
import MapPage from "./MapPage";
import { RequestInputPage } from "./RequestInputPage";
import SidebarAOIDrawPage from "./SidebarAOIDraw";
import SidebarGeofenceDrawPage from "./SidebarGeofenceDraw";
import UnreadAlertHistoryPage from "./UnreadAlertHistoryPage";
import AllAlertHistoryPage from "./AllAlertHistoryPage";
import AOIEditPage from "./AOIEditPage";


function App() {
  return (
    <Routes>
      <Route path="/" element={<MapPage />} />
      <Route path="/drawAOIsidebar" element={<SidebarAOIDrawPage />} />
      <Route path="/drawGeofenceSidebar" element={<SidebarGeofenceDrawPage />} />
      <Route path="/inputs" element={<RequestInputPage />} />
      <Route path="/alerts/history/unread" element={<UnreadAlertHistoryPage/>} />
      <Route path="/alerts/history/all" element={<AllAlertHistoryPage/>} />
    </Routes>
  );
}

export default App;