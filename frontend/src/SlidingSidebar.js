import {
    Drawer,
} from "@mui/material";

import AOISidebar from "./AOISidebar";
import GeofenceSidebar from "./GeofenceSidebar";

export default function SlidingSidebar({
    mode,
    open,
    close,
    ...props
}) {
    return (
        <Drawer
            anchor="left"
            open={open}
            variant="persistent"
            sx={{
                zIndex: 1100,
                "& .MuiDrawer-paper": {
                    width: 320,
                    left: 40,
                    top: 42,
                    height: "calc(100% - 48px)",
                    padding: 2,
                    zIndex: 1100,
                },
            }}
        >
            {mode === "aoi" && (
                <AOISidebar
                    {...props}
                />
            )}

            {mode === "geofence" && (
                <GeofenceSidebar
                    {...props}
                />
            )}
        </Drawer>
    );
}