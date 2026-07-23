import "leaflet/dist/leaflet.css";
import "./styles.css";

import {
    MapContainer,
    TileLayer
} from "react-leaflet";

import { useEffect, useState } from "react";
import { useParams } from "react-router";

import {
    get_ship_using_data_id,
    get_ship_location_history,
    get_all_AOI,
    get_all_geofences
} from "./utils";

import {
    ShipMarkers,
    CourseDirMarkers
} from "./shipmarkers";

import {
    RenderAOIs,
    RenderGeofences
} from "./Boundsrenders";

import {
    MapStateSaver
} from "./screenbounds";


export default function VesselMapPage() {

    const { vessel_data_id } = useParams();

    const [ship, setShip] = useState(null);
    const [location, setLocation] = useState(null);

    const [aoiData, setAoiData] = useState([]);
    const [geofenceData, setGeofenceData] = useState([]);


    useEffect(() => {

        async function load() {

            const vessel =
                await get_ship_using_data_id({
                    vessel_data_id
                });


            const history =
                await get_ship_location_history({
                    vessel_data_id
                });


            if (
                vessel?.data &&
                history?.data?.length
            ) {

                const latest =
                    history.data[0];


                setShip({
                    ...vessel.data,
                    latitude:
                        latest.latitude,
                    longitude:
                        latest.longitude,
                    heading_deg:
                        latest.heading_deg,
                    course_deg:
                        latest.course_deg,
                    speed_knots:
                        latest.speed_knots,
                    timestamp:
                        latest.timestamp,
                    nav_status:
                        latest.nav_status,
                    rate_of_turn:
                        latest.rate_of_turn
                });

                setLocation([
                    latest.latitude,
                    latest.longitude
                ]);

            }


            const aois =
                await get_all_AOI();

            const geofences =
                await get_all_geofences();


            setAoiData(
                aois?.data ?? []
            );

            setGeofenceData(
                geofences?.data ?? []
            );

        }


        load();

    }, [vessel_data_id]);



    if (!ship || !location) {
        return <div>Loading vessel...</div>;
    }


    return (

        <MapContainer
            center={location}
            zoom={15}
            scrollWheelZoom
        >

            <MapStateSaver/>


            <TileLayer
                url=
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />


            <ShipMarkers
                shipdata={[ship]}
            />


            <CourseDirMarkers
                shipdata={[ship]}
            />


            {
                aoiData.length > 0 &&
                <RenderAOIs
                    aoicoordsdata={aoiData}
                />
            }


            {
                geofenceData.length > 0 &&
                <RenderGeofences
                    geofencecoordsdata={geofenceData}
                />
            }


        </MapContainer>

    );

}
