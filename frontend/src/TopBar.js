import { useNavigate } from "react-router";
import "./TopBar.css";

export default function TopBar() {
    const navigate = useNavigate();

    const buttons = [
        {
            label: "Map",
            path: "/",
        },
        {
            label: "Vessels",
            path: "/vessels",
        },
        {
            label: "Inputs",
            path: "/inputs",
        },
        {
            label: "Draw AOI",
            path: "/drawAOIsidebar",
        },
        {
            label: "Draw Geofence",
            path: "/drawGeofenceSidebar",
        },
        {
            label: "Unread Alerts",
            path: "/alerts/history/unread",
        },
        {
            label: "All Alerts",
            path: "/alerts/history/all",
        },
    ];

    return (
        <div className="topbar">
            {buttons.map((button) => (
                <button
                    key={button.path}
                    className="topbar-button"
                    onClick={() => navigate(button.path)}
                >
                    {button.label}
                </button>
            ))}
        </div>
    );
}