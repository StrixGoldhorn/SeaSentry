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
        { label: "AOIs", path: "/aois" },
        { label: "Geofences", path: "/geofences" },
        { label: "Add via coords", path: "/input/aoigeofence" },
        { label: "VOIs", path: "/input/voi" },
        { label: "Alert Rules", path: "/input/alert-rules" },
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
                        variant="scrollable"
                        allowScrollButtonsMobile
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