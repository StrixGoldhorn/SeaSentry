import { useNavigate, useLocation } from "react-router";
import {
    AppBar,
    Toolbar,
    Tabs,
    Tab,
    Typography,
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
        { label: "Unread Alerts", path: "/alerts/history/unread" },
        { label: "All Alerts", path: "/alerts/history/all" },
    ];

    const currentTab =
        pages.find((p) => location.pathname === p.path)?.path || false;

    return (
        <>
        <AppBar position="fixed" elevation={1}>
            <Toolbar
                variant="dense"
                sx={{
                    minHeight: 35,
                    px: 2,
                }}
            >

                <Tabs
                    value={currentTab}
                    onChange={(_, value) => navigate(value)}
                    textColor="inherit"
                    indicatorColor="secondary"
                    sx={{
                        minHeight: 35,
                        "& .MuiTabs-indicator": {
                            height: 3,
                        },
                    }}
                >
                    {pages.map((page) => (
                        <Tab
                            key={page.path}
                            value={page.path}
                            label={page.label}
                            sx={{
                                minHeight: 35,
                                textTransform: "none",
                                fontSize: "0.9rem",
                                px: 2,
                            }}
                        />
                    ))}
                </Tabs>
            </Toolbar>
        </AppBar>
        <Toolbar
            variant="dense"
            sx={{
                minHeight: 44,
            }}
        />
        </>
    );
}