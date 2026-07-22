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
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import FilterAltIcon from '@mui/icons-material/FilterAlt';

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
                    className="thin-sidebar-button"
                >
                    <ListItemIcon className="thin-sidebar-icon">
                        <SatelliteAltIcon />
                    </ListItemIcon>
                </ListItemButton>

                <ListItemButton
                    onClick={() => onSelect("export")}
                    className="thin-sidebar-button"
                >
                    <ListItemIcon className="thin-sidebar-icon">
                        <FileDownloadIcon />
                    </ListItemIcon>
                </ListItemButton>

                <ListItemButton
                    onClick={() => onSelect("filter")}
                    className="thin-sidebar-button"
                >
                    <ListItemIcon className="thin-sidebar-icon">
                        <FilterAltIcon />
                    </ListItemIcon>
                </ListItemButton>

            </List>
        </Drawer>
    );
}