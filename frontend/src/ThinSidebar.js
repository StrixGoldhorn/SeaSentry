import {
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
} from "@mui/material";

import CropIcon from '@mui/icons-material/Crop';
import FenceIcon from '@mui/icons-material/Fence';

export default function ThinSidebar({
    onSelect,
}) {
    return (
        <Drawer
            variant="permanent"
            anchor="left"
            sx={{
                width: 40,
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                    width: 40,
                    top: 42,
                    height: "calc(100% - 48px)",
                    overflowX: "hidden",
                    backgroundColor: "darkblue",
                    color: "white",
                },
            }}
        >
            <List>

                <ListItemButton
                    onClick={() => onSelect("aoi")}
                    sx={{
                        color: "white",
                        justifyContent: "center",

                        "&:hover": {
                            backgroundColor: "#3949ab",
                        },

                        "&.Mui-selected": {
                            backgroundColor: "#303f9f",
                        },
                    }}
                >
                    <ListItemIcon 
                        sx={{
                            color: "white",
                            minWidth: "0",
                            justifyContent: "center",
                        }}>
                        <CropIcon />
                    </ListItemIcon>
                </ListItemButton>

                <ListItemButton
                    onClick={() => onSelect("geofence")}
                    sx={{
                        color: "white",
                        justifyContent: "center",

                        "&:hover": {
                            backgroundColor: "#3949ab",
                        },

                        "&.Mui-selected": {
                            backgroundColor: "#303f9f",
                        },
                    }}
                >
                    <ListItemIcon
                        sx={{
                            color: "white",
                            minWidth: "0",
                            justifyContent: "center",
                        }}>
                        <FenceIcon />
                    </ListItemIcon>
                </ListItemButton>

            </List>
        </Drawer>
    );
}