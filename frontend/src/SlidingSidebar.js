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
                "& .MuiDrawer-paper": {
                    width: 320,
                    left: 40,
                    top: 42,
                    height: "calc(100% - 48px)",
                    padding: 2,
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