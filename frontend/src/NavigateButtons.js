import { useNavigate } from "react-router";

export function NavigateToInputsButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/inputs")}
      style={{
        position: "absolute",
        top: "20px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Go To Inputs
    </button>
  );
}

export function NavigateToMapButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/ ")}
      style={{
        position: "absolute",
        top: "20px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Go To Map
    </button>
  );
}

export function NavigateToAOIDrawButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/drawAOIsidebar")}
      style={{
        position: "absolute",
        top: "70px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Draw AOI
    </button>
  );
}

export function NavigateToGeofenceDrawButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/drawGeofenceSidebar")}
      style={{
        position: "absolute",
        top: "120px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Draw Geofence
    </button>
  );
}

export function NavigateToUnreadAlertHistoryButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/alerts/history/unread")}
      style={{
        position: "absolute",
        top: "170px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Go to Alert History
    </button>
  );
}

export function NavigateToAllAlertHistoryButton() {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate("/alerts/history/all")}
      style={{
        position: "absolute",
        top: "70px",
        right: "20px",
        zIndex: 1000,
        padding: "10px 15px",
      }}
    >
      Go to All Alert History
    </button>
  );
}