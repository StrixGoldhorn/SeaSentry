import { Icon } from "leaflet";
import { Marker, Popup } from "react-leaflet";
import CursorIcon from "./cursor.png";

const customIcon = new Icon({
  iconUrl: CursorIcon,
  iconSize: [38, 38]
})

export function ShipMarkers(shipdata) {
    if (!Array.isArray(shipdata)) {
        return null;
    }
    
    return (shipdata.map((ship) => (
        <Marker
        position = {[ship.latitude, ship.longitude]}
        icon = {customIcon}
        >
            <Popup>
                <div style={{ padding: '10px' }}>
                <h4>{ship.ship_name}</h4>
                <ul>
                    <li>MMSI: {ship.mmsi}</li>
                    <li>IMO: {ship.imo}</li>
                    <li>Flag: {ship.flag}</li>
                    <li>Speed (kts): {ship.speed_knots}</li>
                    <li>Course (deg): {ship.course_deg}</li>
                    <li>Heading (deg): {ship.heading_deg}</li>
                    <li>Timestamp of log: {ship.timestamp}</li>
                </ul>
                </div>
            </Popup>
        </Marker>
        )))
}