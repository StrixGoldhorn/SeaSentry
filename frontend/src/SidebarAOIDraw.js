import "leaflet/dist/leaflet.css";
import './styles.css';
import { MapContainer, TileLayer, Marker, Popup, Rectangle, Polygon, useMapEvent, useMapEvents } from 'react-leaflet';
import { Icon } from "leaflet";
import { useEffect, useState } from "react";
import { ShipMarkers, CourseDirMarkers } from "./shipmarkers.js";
import * as utils from './utils.js';
import { MapBoundsTracker, MapStateSaver, getMapCenter, getMapZoom } from "./screenbounds.js";
import { RenderAOIs, RenderGeofences } from "./Boundsrenders.js";

import AOIPolygonDrawerNew from "./AOIPolygonDrawerNew";
import AOISidebar from "./AOISidebar";

export default function SidebarAOIDrawPage() {

    //useStates
    const [shipData, setshipData] = useState({});
    const [aoiData, setaoiData] = useState({});
    const [geofenceData, setgeofenceData] = useState({});
    const [mapBounds, setmapBounds] = useState({lat_min:0, lat_max:0, long_min:0, long_max:0});

    const [drawing, setDrawing] = useState(false);

    const [coords, setCoords] = useState([]);

    const [name, setName] = useState("");

    const [desc, setDesc] = useState("");
    
      //useEffects
      useEffect(() => {
        utils.get_ships_on_screen(mapBounds)
          .then(fetchdata => {
              if (fetchdata === null) {
                console.log("API did not return data");
              } else {
                setshipData(fetchdata);
              }
            })
      }, [mapBounds]);
    
      useEffect(() => {
        utils.get_all_AOI()
        .then(fetchdata => {
          if (fetchdata === null) {
            console.log("API did not return data");
          } else {
            setaoiData(fetchdata);
          }
        })
      }, [mapBounds]);
    
      useEffect(() => {
        utils.get_all_geofences()
        .then(fetchdata => {
          if (fetchdata === null) {
            console.log("API did not return data");
          } else {
            setgeofenceData(fetchdata);
          }
        })
      }, [mapBounds]);

    
    let initialCenter = getMapCenter();
    let initialZoom = getMapZoom();

    return (
        <div
        className="app"
            style={{
                display: "flex",
                height: "100vh",
                width: "100vw"
            }}
        >

            <div className="sidebar">
            <AOISidebar
                drawing={drawing}
                setDrawing={setDrawing}
                coords={coords}
                setCoords={setCoords}
                name={name}
                setName={setName}
                desc={desc}
                setDesc={setDesc}
            />
            </div>


            <div
            className="map-container"
                style={{
                    flex: 1
                }}
            >
                <MapContainer
                    center={initialCenter} zoom={initialZoom}
                    style={{
                        height: "100%",
                        width: "100%"
                    }}
                >
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    <MapBoundsTracker onBoundsChange={setmapBounds} />
                    {shipData?.data && (<ShipMarkers shipdata={shipData.data} />)}
                    {shipData?.data && (<CourseDirMarkers shipdata={shipData.data} />)}
                    {aoiData?.data && (<RenderAOIs aoicoordsdata={aoiData.data} />)}
                    {geofenceData?.data && (<RenderGeofences geofencecoordsdata={geofenceData.data} />)}

                    <AOIPolygonDrawerNew
                        drawing={drawing}
                        coords={coords}
                        setCoords={setCoords}
                    />
                </MapContainer>
              </div>
          </div>
    );
}