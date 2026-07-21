import "./TopBar.css";

import { useNavigate, useLocation } from "react-router";
import {
    AppBar,
    Toolbar,
    Tabs,
    Tab,
} from "@mui/material";

export default function TopBar() {
    const navigate = useNavigate();
    const location = useLocation();

    const pages = [
        { label: "Map", path: "/" },
        { label: "Vessels", path: "/vessels" },
        { label: "Inputs", path: "/inputs" },
        { label: "Draw AOI", path: "/drawAOIsidebar" },
        { label: "Draw Geofence", path: "/drawGeofenceSidebar" },
        { label: "All Alerts", path: "/alerts/history/all" },
    ];

    const currentTab =
        pages.find((p) => location.pathname === p.path)?.path || false;

    return (
        <>
            <AppBar
                position="fixed"
                elevation={1}
                className="topbar"
            >
                <Toolbar
                    variant="dense"
                    className="topbar-toolbar"
                >
                    <Tabs
                        value={currentTab}
                        onChange={(_, value) => navigate(value)}
                        textColor="inherit"
                        indicatorColor="secondary"
                        className="topbar-tabs"
                    >
                        {pages.map((page) => (
                            <Tab
                                key={page.path}
                                value={page.path}
                                label={page.label}
                            />
                        ))}
                    </Tabs>
                </Toolbar>
            </AppBar>

            <Toolbar
                variant="dense"
                className="topbar-offset"
            />
        </>
    );
}