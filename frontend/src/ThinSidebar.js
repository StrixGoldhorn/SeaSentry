import "./ThinSidebar.css";

import {
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText
} from "@mui/material";

import CropIcon from "@mui/icons-material/Crop";
import FenceIcon from "@mui/icons-material/Fence";
import SatelliteAltIcon from "@mui/icons-material/SatelliteAlt";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import FilterAltIcon from '@mui/icons-material/FilterAlt';

const menuItems = [
    { id: "aoi", icon: <CropIcon />, label: "Add AOI" },
    { id: "geofence", icon: <FenceIcon />, label: "Add Geofence" },
    { id: "imagery", icon: <SatelliteAltIcon />, label: "Satellite Imagery" },
    { id: "export", icon: <FileDownloadIcon />, label: "Export Area" },
    { id: "filter", icon: <FilterAltIcon  />, label: "Filter Shiptypes" },
];

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
                {menuItems.map((item) => (
                    <ListItemButton
                        key={item.id}
                        onClick={() => onSelect(item.id)}
                        className="thin-sidebar-button"
                    >
                        <ListItemIcon className="thin-sidebar-icon">
                        {item.icon}
                        </ListItemIcon>
                        <ListItemText 
                        primary={item.label} 
                        className="thin-sidebar-text"
                        primaryTypographyProps={{ 
                            style: { color: "var(--pri)", whiteSpace: "nowrap" } 
                        }}
                        />
                    </ListItemButton>
                ))}

            </List>
        </Drawer>
    );
}