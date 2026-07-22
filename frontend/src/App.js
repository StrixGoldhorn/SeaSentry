import { Routes, Route } from "react-router";
import TopBar from "./TopBar";
import MapPage from "./MapPage";
import { RequestInputPage } from "./RequestInputPage";
import SidebarAOIDrawPage from "./SidebarAOIDraw";
import SidebarGeofenceDrawPage from "./SidebarGeofenceDraw";
import AllAlertHistoryPage from "./AllAlertHistoryPage";
import VesselTablePage from "./VesselTablePage";
import AOITablePage from "./AOITablePage";
import GeofenceTablePage from "./GeofenceTablePage";
import VesselHistoryMap from "./VesselHistoryMap";
import VesselHistoryPage from "./VesselHistoryPage";


function App() {
  return (
    <>
    <TopBar/>
    <Routes>
      <Route path="/" element={<MapPage />} />
      <Route path="/drawAOIsidebar" element={<SidebarAOIDrawPage />} />
      <Route path="/drawGeofenceSidebar" element={<SidebarGeofenceDrawPage />} />
      <Route path="/inputs" element={<RequestInputPage />} />
      <Route path="/aois" element={<AOITablePage />} />
      <Route path="/geofences" element={<GeofenceTablePage />} />
      <Route path="/vessels" element={<VesselTablePage />} />
      <Route
        path="/vessel-history/:vesselDataId"
        element={<VesselHistoryPage />}
      />
      <Route path="/alerts/history/all" element={<AllAlertHistoryPage/>} />
    </Routes>
    </>
  );
}

export default App;