import { Icon } from "leaflet";
import { Marker, Popup } from "react-leaflet";
import CursorIcon from "./cursor.png";
import LineIcon from "./dotted-barline.png";
import "leaflet-rotatedmarker";
import "./styles.css";

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

const getTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown'; // should never happen because timestamp is requried in the db
    
    const now = new Date();
    const past = new Date(timestamp);

    const diffSec = Math.floor((now - past) / 1000);
    if (diffSec < 60) return `${diffSec} second${diffSec !== 1 ? 's' : ''} ago`;
    
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
    
    const diffHrs = Math.floor(diffMin / 60);
    if (diffHrs < 24) return `${diffHrs} hour${diffHrs !== 1 ? 's' : ''} ago`;
    
    const diffDay = Math.floor(diffHrs / 24);
    return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
};

export function ShipMarkers({ shipdata }) {
    if (!Array.isArray(shipdata)) {
        return null;
    }
    
    return (shipdata.map((ship) => (
        <Marker
        key={ship.vessel_data_id}
        position = {[ship.latitude, ship.longitude]}
        icon = {customIcon}
        rotationOrigin="center"
        rotationAngle={shipDegCheck(ship.heading_deg)}
        zIndexOffset={600}
        >
            <Popup autoPan={false} className="vesselpopup">
                <div>
                    <h3>{ship.ship_name}</h3>
                    {ship.ship_type != null && ship.ship_type !== '' && <p><i>Type: {ship.ship_type}</i></p>}
                    <hr></hr>

                    <div class="info">
                        {ship.ship_name != null && ship.ship_name !== '' && <p>Ship Name: {ship.ship_name}</p>}
                        {ship.ship_type != null && ship.ship_type !== '' && <p>Ship Type: {ship.ship_type}</p>}
                        <p>MMSI: {ship.mmsi}</p>
                        <p>IMO: {ship.imo}</p>
                        {ship.beam_meters != null && ship.beam_meters !== '' && <p>Beam length (m): {ship.beam_meters}</p>}
                        {ship.length_meters != null && ship.length_meters !== '' && <p>Vessel length (m): {ship.length_meters}</p>}
                        {ship.flag != null && ship.flag !== '' && <p>Flag: {ship.flag}</p>}
                        {ship.speed_knots != null && ship.speed_knots !== '' && <p>Speed (kts): {ship.speed_knots}</p>}
                        {ship.course_deg != null && ship.course_deg !== '' && <p>Course (deg): {ship.course_deg}</p>}
                        {ship.heading_deg != null && ship.heading_deg !== '' && <p>Heading (deg): {ship.heading_deg}</p>}
                        {ship.rate_of_turn != null && ship.rate_of_turn !== '' && <p>Rate of turn (deg/min): {ship.rate_of_turn}</p>}
                        {ship.nav_status != null && ship.nav_status !== '' && <p>Navigation Status: {ship.nav_status}</p>}
                        {ship.user_tags != null && ship.user_tags !== '' && <p>User Tags: {ship.user_tags}</p>}
                    </div>

                    <i>Last pinged: {getTimeAgo(new Date(ship.timestamp))}</i>
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
        key={ship.vessel_data_id}
        position = {[ship.latitude, ship.longitude]}
        icon = {lineIcon}
        rotationOrigin="center"
        rotationAngle={shipDegCheck(ship.course_deg)}
        >
            
        </Marker>
        )))
}