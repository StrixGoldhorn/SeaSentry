import AOIPanel from "./AOIForm";
import GeofencePanel from "./GeofenceForm";

export default function AOIGeofenceInputPage() {
    return (
        <div style={{ padding: "20px" }}>
            <AOIPanel />
            <GeofencePanel />
        </div>
    );
}
