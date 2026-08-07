import {
    Drawer,
    IconButton,
    Box,
} from "@mui/material";

import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";

import AOISidebar from "./AOISidebar";
import GeofenceSidebar from "./GeofenceSidebar";
import CopernicusImageryLayerControl from "./CopernicusImageryLayerControl";
import ExportAreaSidebar from "./ExportAreaSidebar";
import FilterSidebar from "./FilterSidebar";

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
                    width: 350,
                    left: 40,
                    top: 42,
                    height: "calc(100% - 40px)",
                    padding: 2,
                    zIndex: 1100,
                },
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "flex-end",
                    mb: 1,
                }}
            >
                <IconButton onClick={close}>
                    <ChevronLeftIcon />
                </IconButton>
            </Box>
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

            {mode === "imagery" && (
                <CopernicusImageryLayerControl
                    instanceId={props.instanceId}
                    setInstanceId={props.setInstanceId}
                    selectedLayer={props.selectedLayer}
                    setSelectedLayer={props.setSelectedLayer}
                />
            )}

            {mode === "export" && (
                <ExportAreaSidebar
                    {...props}
                />
            )}

            {mode === "filter" && <FilterSidebar {...props} />}

        </Drawer>
    );
}