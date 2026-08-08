import * as L from "leaflet";
import { Marker, Popup } from "react-leaflet";
import "leaflet-rotatedmarker";
import "./styles.css";
import { useNavigate } from "react-router";
import { useState } from "react";
import VesselEditDialog from "./VesselEditDialog";
import { memo } from 'react';

function getColorFromShiptype(ship_type) {
    if (ship_type == null) {
        return "#707070"
    }
    const colorMap = {
        "Cargo" : "#e6c72c",
        "Fishing" : "#88f886",
        "High Speed Craft" : "#c0f424",
        "Law Enforcement" : "#2548e4",
        "Medical Transport" : "#d20d0d",
        "Military" : "#e70000",
        "Passenger" : "#ce49b5",
        "Pleasure Craft" : "#ce49b5",
        "Sailing" : "#bcd4d4",
        "SAR" : "#d20d0d",
        "Tanker" : "#e6c72c",
        "Tug" : "#41b14a"
    }
    return colorMap[ship_type] || "#707070";
}

export function createShipIcon(shipname, hasHeading, ship_type, size = 20) {
    const color = getColorFromShiptype(ship_type)

    if (hasHeading) {
        const shipWidth = size * 0.75;
        const shipHeight = size;

        const shipPoly = "polygon(50% 0%, 100% 40%, 100% 100%, 0 100%, 0 40%)"

        const shapeStyle = `
            width: calc(100% - 2px);
            height: calc(100% - 2px);
            background: ${color}; 
            clip-path: ${shipPoly};
        `;

        const outlineStyle = `
            width: ${shipWidth}px; 
            height: ${shipHeight}px; 
            background: black; 
            clip-path: ${shipPoly};
            display: flex;
            justify-content: center;
            align-items: center;
        `;

        return L.divIcon({
            className: 'ship-icon',
            html: `<div style="${outlineStyle}"><div style="${shapeStyle}"></div></div>`,
            iconSize: [shipWidth, shipHeight],
            iconAnchor: [shipWidth / 2, shipHeight / 2]
        });


    } else {
        const circleSize = size * 0.75;
        const offset = (size - circleSize) / 2;

        const shapeStyle = `
            width: ${circleSize}px; 
            height: ${circleSize}px; 
            background: ${color}; 
            border: 1.5px solid black;
            border-radius: 50%;
            margin: ${offset}px;
            box-sizing: border-box;
        `;

        return L.divIcon({
            className: 'ship-icon',
            html: `<div style="${shapeStyle}"></div>`,
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2]
        });
    }


}

function createCourseLineIcon(color, size = 40) {
    const halfSize = size / 2;
    return L.divIcon({
        className: 'course-line-icon',
        html: `<div style="
            width: 2px; 
            height: ${size*0.5}px; 
            background: black;
            margin-left: ${halfSize - 1}px;
        "></div>`,
        iconSize: [size, size],
        iconAnchor: [halfSize, halfSize]
    });
}

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

const getNavStatusString = (nav_status) => {
    const statusMap = {
        0: "Under way using engine",
        1: "At anchor",
        2: "Not under command",
        3: "Restricted manoeuverability",
        4: "Constrained by draught",
        5: "Moored",
        6: "Aground",
        7: "Engaged in fishing",
        8: "Under way sailing",
        9: "Reserved",
        10: "Reserved",
        11: "Reserved",
        12: "Reserved",
        13: "Reserved",
        14: "AIS-SART",
        15: "" // technically shouldn't even happen
    };

    if (nav_status !== null && nav_status !== undefined && statusMap.hasOwnProperty(nav_status)) {
        return statusMap[nav_status];
    }

    return "Unknown";
}

const isShipEqual = (prevProps, nextProps) => {
    const prev = prevProps.ship;
    const next = nextProps.ship;

    if (prev.vessel_data_id !== next.vessel_data_id) return false;

    const prevAlerts = prevProps.alerts || [];
    const nextAlerts = nextProps.alerts || [];
    if (prevAlerts.length !== nextAlerts.length) return false;
    for (let i = 0; i < prevAlerts.length; i++) {
        if (prevAlerts[i].alert_history_id !== nextAlerts[i].alert_history_id) return false;
    }

    return (
        prev.latitude === next.latitude &&
        prev.longitude === next.longitude &&
        prev.heading_deg === next.heading_deg &&
        prev.course_deg === next.course_deg &&
        prev.ship_type === next.ship_type &&
        prev.speed_knots === next.speed_knots &&
        prev.nav_status === next.nav_status &&
        prev.timestamp === next.timestamp
    );
};

const isCourseEqual = (prevProps, nextProps) => {
    const prev = prevProps.ship;
    const next = nextProps.ship;

    if (prev.vessel_data_id !== next.vessel_data_id) return false;

    return (
        prev.latitude === next.latitude &&
        prev.longitude === next.longitude &&
        prev.course_deg === next.course_deg &&
        prev.ship_type === next.ship_type
    );
};

const ShipMarker = memo(function ShipMarker({ ship, alerts, onMarkAlertRead }) {
    const navigate = useNavigate();
    const [isEditOpen, setIsEditOpen] = useState(false);

    const hasHeading =
        ship.heading_deg != null &&
        ship.heading_deg !== "";

    const customIcon = createShipIcon(
        ship.ship_name,
        hasHeading,
        ship.ship_type
    );

    return (
        <>
            <Marker
                position={[ship.latitude, ship.longitude]}
                icon={customIcon}
                rotationOrigin="center"
                rotationAngle={shipDegCheck(ship.heading_deg)}
                zIndexOffset={600}
            >
                <Popup autoPan={false} className="vesselpopup">
                    <div>
                        <h3>{ship.ship_name}</h3>
                        {ship.ship_type != null && ship.ship_type !== '' && <p><i>Type: {ship.ship_type}</i></p>}
                        <hr />
                        <div className="info">
                            <p>MMSI: {ship.mmsi}</p>
                            <p>IMO: {ship.imo}</p>
                            {ship.beam_meters != null && ship.beam_meters !== '' && <p>Beam length (m): {ship.beam_meters}</p>}
                            {ship.length_meters != null && ship.length_meters !== '' && <p>Vessel length (m): {ship.length_meters}</p>}
                            {ship.flag != null && ship.flag !== '' && <p>Flag: {ship.flag}</p>}
                            {ship.speed_knots != null && ship.speed_knots !== '' && <p>Speed (kts): {ship.speed_knots}</p>}
                            {ship.course_deg != null && ship.course_deg !== '' && <p>Course (deg): {ship.course_deg}</p>}
                            {ship.heading_deg != null && ship.heading_deg !== '' && <p>Heading (deg): {ship.heading_deg}</p>}
                            {ship.rate_of_turn != null && ship.rate_of_turn !== '' && <p>Rate of turn (deg/min): {ship.rate_of_turn}</p>}
                            {ship.nav_status != null && ship.nav_status !== '' && ship.nav_status !== 15 && <p>Navigation Status: {getNavStatusString(ship.nav_status)}</p>}
                            {ship.user_tags != null && ship.user_tags !== '' && <p>User Tags: {ship.user_tags.join(', ')}</p>}
                        </div>
                        <i>Last pinged: {getTimeAgo(new Date(ship.timestamp))}</i><br />
                        <div>
                            <button
                                onClick={() => {
                                    navigate(
                                        `/vessel-history/${ship.vessel_data_id}`,
                                    );
                                }}
                            >
                                View History
                            </button>
                            <button
                                onClick={() => setIsEditOpen(true)}
                            >
                                Edit
                            </button>
                        </div>
                    </div>
                </Popup>
            </Marker>
            {isEditOpen && (
                <VesselEditDialog
                    ship={ship}
                    onClose={() => setIsEditOpen(false)}
                    onSaved={() => {
                        setIsEditOpen(false);
                    }}
                />
            )}
        </>
    );
}, isShipEqual);

const CourseLineMarker = memo(function CourseLineMarker({ ship }) {
    const lineIcon = createCourseLineIcon(getColorFromShiptype(ship.ship_type));
    return (
        <Marker
            position={[ship.latitude, ship.longitude]}
            icon={lineIcon}
            rotationOrigin="center"
            rotationAngle={shipDegCheck(ship.course_deg)}
            interactive={false}
        />
    );
}, isCourseEqual);

export function ShipMarkers({ shipdata, alertVessels, onMarkAlertRead }) {
    if (!Array.isArray(shipdata)) {
        return null;
    }

    return shipdata.map(ship => (
        <ShipMarker
            key={ship.vessel_data_id}
            ship={ship}
            alerts={alertVessels ? alertVessels.get(String(ship.mmsi)) : null}
            onMarkAlertRead={onMarkAlertRead}
        />
    ));
}

export function CourseDirMarkers({ shipdata }) {
    if (!Array.isArray(shipdata)) {
        return null;
    }

    return shipdata
        // filter out those with no course data
        .filter(ship => ship.course_deg != null && ship.course_deg !== '' && ship.course_deg !== 0)
        .map((ship) => (
            <CourseLineMarker key={`course-${ship.vessel_data_id}`} ship={ship} />
        ));
}

// export function ShipMarkers({ shipdata }) {
//     if (!Array.isArray(shipdata)) {
//         return null;
//     }

//     return shipdata.map((ship) => {
//         const hasHeading = ship.heading_deg != null && ship.heading_deg !== '';
//         const customIcon = createShipIcon(ship.ship_name, hasHeading, ship.ship_type);

//         return (
//             <Marker
//                 key={ship.vessel_data_id}
//                 position={[ship.latitude, ship.longitude]}
//                 icon={customIcon}
//                 rotationOrigin="center"
//                 rotationAngle={shipDegCheck(ship.heading_deg)}
//                 zIndexOffset={600}
//             >
//                 <Popup autoPan={false} className="vesselpopup">
//                     <div>
//                         <h3>{ship.ship_name}</h3>
//                         {ship.ship_type != null && ship.ship_type !== '' && <p><i>Type: {ship.ship_type}</i></p>}
//                         <hr />
//                         <div className="info">
//                             <p>MMSI: {ship.mmsi}</p>
//                             <p>IMO: {ship.imo}</p>
//                             {ship.beam_meters != null && ship.beam_meters !== '' && <p>Beam length (m): {ship.beam_meters}</p>}
//                             {ship.length_meters != null && ship.length_meters !== '' && <p>Vessel length (m): {ship.length_meters}</p>}
//                             {ship.flag != null && ship.flag !== '' && <p>Flag: {ship.flag}</p>}
//                             {ship.speed_knots != null && ship.speed_knots !== '' && <p>Speed (kts): {ship.speed_knots}</p>}
//                             {ship.course_deg != null && ship.course_deg !== '' && <p>Course (deg): {ship.course_deg}</p>}
//                             {ship.heading_deg != null && ship.heading_deg !== '' && <p>Heading (deg): {ship.heading_deg}</p>}
//                             {ship.rate_of_turn != null && ship.rate_of_turn !== '' && <p>Rate of turn (deg/min): {ship.rate_of_turn}</p>}
//                             {ship.nav_status != null && ship.nav_status !== '' && ship.nav_status !== 15 && <p>Navigation Status: {getNavStatusString(ship.nav_status)}</p>}
//                             {ship.user_tags != null && ship.user_tags !== '' && <p>User Tags: {ship.user_tags.join(', ')}</p>}
//                         </div>
//                         <i>Last pinged: {getTimeAgo(new Date(ship.timestamp))}</i>
//                     </div>
//                 </Popup>
//             </Marker>
//         );
//     });
// }
