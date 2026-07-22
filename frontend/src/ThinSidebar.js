import "./ThinSidebar.css";

import {
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
} from "@mui/material";

import CropIcon from "@mui/icons-material/Crop";
import FenceIcon from "@mui/icons-material/Fence";
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";

export default function ThinSidebar({ onSelect }) {
    return (
        <Drawer
            variant="permanent"
            anchor="left"
            classes={{
                paper: "thin-sidebar-paper",
            }}
        >
            <List>
                <ListItemButton
                    onClick={() => onSelect("aoi")}
                    className="thin-sidebar-button"
                >
                    <ListItemIcon className="thin-sidebar-icon">
                        <CropIcon />
                    </ListItemIcon>
                </ListItemButton>

                <ListItemButton
                    onClick={() => onSelect("geofence")}
                    className="thin-sidebar-button"
                >
                    <ListItemIcon className="thin-sidebar-icon">
                        <FenceIcon />
                    </ListItemIcon>
                </ListItemButton>

                <ListItemButton
                    onClick={() => onSelect("imagery")}
                    sx={{ color: "white", justifyContent: "center" }}
                >
                    <ListItemIcon
                        sx={{
                            color: "white",
                            minWidth: 0,
                            justifyContent: "center",
                        }}
                    >
                        <SatelliteAltIcon />
                    </ListItemIcon>
                </ListItemButton>
            </List>
        </Drawer>
    );
}