import { Icon } from "leaflet";
import { Marker, Popup } from "react-leaflet";
import CursorIcon from "./cursor.png";
import LineIcon from "./dotted-barline.png";
import "leaflet-rotatedmarker";

const customIcon = new Icon({
  iconUrl: CursorIcon,
  iconSize: [30, 30]
})

const lineIcon = new Icon({
  iconUrl: LineIcon,
  iconSize: [20, 50]
})

function shipDegCheck(deg) {
    if (deg === null) {
        return 0;
    }
    return deg;
}

export function ShipMarkers({ shipdata }) {
    if (!Array.isArray(shipdata)) {
        return null;
    }
    
    return (shipdata.map((ship) => (
        <Marker
        position = {[ship.latitude, ship.longitude]}
        icon = {customIcon}
        rotationOrigin="center"
        rotationAngle={shipDegCheck(ship.heading_deg)}
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

export function CourseDirMarkers({ shipdata }) {
    if (!Array.isArray(shipdata)) {
        return null;
    }
    
    return (shipdata.map((ship) => (
        <Marker
        position = {[ship.latitude, ship.longitude]}
        icon = {lineIcon}
        rotationOrigin="center"
        rotationAngle={shipDegCheck(ship.course_deg)}
        >
            
        </Marker>
        )))
}