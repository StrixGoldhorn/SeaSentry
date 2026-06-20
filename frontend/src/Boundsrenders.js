import { PolygonOverlay } from "./Polygon";

export function RenderAOIs ({ aoicoordsdata }) {
    if (!Array.isArray(aoicoordsdata)) {
        return null;
    }

    const aoicolor = "black";

    return (aoicoordsdata.map((aoi) => (

        <PolygonOverlay coords={aoi.area_of_interest_polygon} color={aoicolor} />
    )))
}

export function RenderGeofences ({ geofencecoordsdata }) {
    if (!Array.isArray(geofencecoordsdata)) {
        return null;
    }

    const geofencecolor = "red";

    return (geofencecoordsdata.map((geofence) => (

        <PolygonOverlay coords={geofence.geofence_polygon} color={geofencecolor} />
    )))
}