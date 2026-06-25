import { PolygonOverlay } from "./Polygon";
import { delete_AOI, delete_geofence } from "./utils";



export function RenderAOIs({
    aoicoordsdata,
    refreshAOIs
}) {

    if (!Array.isArray(aoicoordsdata)) {
        return null;
    }

    return aoicoordsdata.map((aoi) => (

        <PolygonOverlay
            key={aoi.area_of_interest_id}
            item={aoi}
            color="black"

            polygonField="area_of_interest_polygon"
            idField="area_of_interest_id"
            nameField="area_of_interest_name"
            descriptionField="area_of_interest_description"
            timestampField="area_of_interest_timestamp"

            deleteFunction={({ id, name }) =>
                delete_AOI({
                    aoi_id: id,
                    aoi_name: name
                })
            }

            refreshFunction={refreshAOIs}

            deleteLabel="Delete AOI"
        />

    ));
}

export function RenderGeofences({
    geofencecoordsdata,
    refreshGeofences
}) {

    if (!Array.isArray(geofencecoordsdata)) {
        return null;
    }

    return geofencecoordsdata.map((geofence) => (

        <PolygonOverlay
            key={geofence.geofence_id}
            item={geofence}
            color="red"

            polygonField="geofence_polygon"
            idField="geofence_id"
            nameField="geofence_name"
            descriptionField="geofence_description"
            timestampField="geofence_timestamp"

            deleteFunction={({ id, name }) =>
                delete_geofence({
                    geofence_id: id,
                    geofence_name: name
                })
            }

            refreshFunction={refreshGeofences}

            deleteLabel="Delete Geofence"
        />

    ));
}

// export function RenderGeofences ({ geofencecoordsdata }) {
//     if (!Array.isArray(geofencecoordsdata)) {
//         return null;
//     }

//     const geofencecolor = "red";

//     return (geofencecoordsdata.map((geofence) => (

//         <PolygonOverlay key={geofence.geofence_id} aoi={aoi} color={geofencecolor} />
//     )))
// }