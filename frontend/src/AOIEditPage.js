import "leaflet/dist/leaflet.css";
import "./styles.css";

import { useEffect, useState } from "react";
import {
    MapContainer,
    TileLayer
} from "react-leaflet";
import * as utils from "./utils";
import { MapBoundsTracker } from "./screenbounds";
import { RenderAOIs } from "./Boundsrenders";
import EditableAOILayer from "./EditableAOILayer";
import { AOIEditSidebar } from "./AOIEditSidebar";

function AOIEditPage() {

    const [mapBounds, setMapBounds] = useState({
        lat_min: 0,
        lat_max: 0,
        long_min: 0,
        long_max: 0
    });

    const [aoiData, setAOIData] = useState({});

    const [editingAOI, setEditingAOI] = useState(null);

    const [editedCoords, setEditedCoords] = useState([]);

    useEffect(() => {
        loadAOIs();
    }, [mapBounds]);

    async function loadAOIs() {

        const data = await utils.get_all_AOI();

        if (data != null) {
            setAOIData(data);
        }

    }

    function startEditing(aoi) {

        setEditingAOI(aoi);

        setEditedCoords(
            aoi.area_of_interest_polygon
        );

    }

    function finishEditing() {

        setEditingAOI(null);

        setEditedCoords([]);

        loadAOIs();

    }

    function cancelEditing() {

        setEditingAOI(null);

        setEditedCoords([]);

    }

    return (

        <div
            style={{
                display: "flex",
                width: "100vw",
                height: "100vh"
            }}
        >

            <MapContainer
                center={[
                    1.2595764399413216,
                    103.8335830126783
                ]}
                zoom={14}
                scrollWheelZoom={true}
                style={{
                    flex: 1
                }}
            >

                <TileLayer
                    attribution='&copy; OpenStreetMap contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapBoundsTracker
                    onBoundsChange={setMapBounds}
                />

                {

                    aoiData?.data && (

                        <RenderAOIs

                            aoicoordsdata={
                                aoiData.data
                            }

                            refreshAOIs={loadAOIs}

                            editing={
                                editingAOI !== null
                            }

                            onEdit={
                                startEditing
                            }

                        />

                    )

                }

                {

                    editingAOI && (

                        <EditableAOILayer

                            coords={
                                editedCoords
                            }

                            setCoords={
                                setEditedCoords
                            }

                        />

                    )

                }

            </MapContainer>

            {

                editingAOI && (

                    <AOIEditSidebar

                        editingAOI={
                            editingAOI
                        }

                        coords={
                            editedCoords
                        }

                        finish={
                            finishEditing
                        }

                        cancel={
                            cancelEditing
                        }

                    />

                )

            }

        </div>

    );

}

export default AOIEditPage;