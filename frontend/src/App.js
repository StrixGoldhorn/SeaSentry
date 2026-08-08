import { Routes, Route } from "react-router";
import TopBar from "./TopBar";
import MapPage from "./MapPage";
import AOIGeofenceInputPage from "./AOIGeofenceInputPage";
import VOIPage from "./VOIPage";
import AlertRulesPage from "./AlertRulesPage";
import SidebarAOIDrawPage from "./SidebarAOIDraw";
import SidebarGeofenceDrawPage from "./SidebarGeofenceDraw";
import AllAlertHistoryPage from "./AllAlertHistoryPage";
import VesselTablePage from "./VesselTablePage";
import AOITablePage from "./AOITablePage";
import GeofenceTablePage from "./GeofenceTablePage";
import VesselHistoryMap from "./VesselHistoryMap";
import VesselHistoryPage from "./VesselHistoryPage";
import VesselMapPage from "./VesselMapPage";


function App() {
  return (
    <>
    <TopBar/>
    <Routes>
      <Route path="/" element={<MapPage />} />
      <Route path="/drawAOIsidebar" element={<SidebarAOIDrawPage />} />
      <Route path="/drawGeofenceSidebar" element={<SidebarGeofenceDrawPage />} />
      <Route path="/input/aoigeofence" element={<AOIGeofenceInputPage />} />
      <Route path="/input/voi" element={<VOIPage />} />
      <Route path="/input/alert-rules" element={<AlertRulesPage />} />
      <Route path="/aois" element={<AOITablePage />} />
      <Route path="/geofences" element={<GeofenceTablePage />} />
      <Route path="/vessels" element={<VesselTablePage />} />
      <Route
        path="/vessel-history/:vesselDataId"
        element={<VesselHistoryPage />}
      />
      <Route
          path="/vessel/:vessel_data_id"
          element={<VesselMapPage />}
      />
      <Route path="/alerts/history/all" element={<AllAlertHistoryPage/>} />
    </Routes>
    </>
  );
}

export default App;