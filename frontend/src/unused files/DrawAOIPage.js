import "leaflet/dist/leaflet.css";
import './css/styles.css';
import { MapContainer, TileLayer, Marker, Popup, Rectangle, Polygon, useMapEvent, useMapEvents } from 'react-leaflet';
import { Icon } from "leaflet";
import CursorIcon from "./cursor.png";
import { useEffect, useState } from "react";
import { ShipMarkers, CourseDirMarkers } from "./shipmarkers.js";
import * as utils from './utils.js';
import { MapBoundsTracker } from "./screenbounds.js";
import { RenderAOIs, RenderGeofences } from "./Boundsrenders.js";
import { NavigateToInputsButton } from "./NavigateButtons.js";
import AOIPolygonDrawer from "./AOIPolygonDrawer";
import GeofencePolygonDrawer from "./GeofencePolygonDrawer.js";



function DrawAOIPage() {

  //useStates
  const [shipData, setshipData] = useState({});
  const [aoiData, setaoiData] = useState({});
  const [geofenceData, setgeofenceData] = useState({});
  const [mapBounds, setmapBounds] = useState({lat_min:0, lat_max:0, long_min:0, long_max:0});


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

  //HTML return
  return (
    <>
    <MapContainer center={[1.2595764399413216, 103.8335830126783]} zoom={14} scrollWheelZoom={true}>
      <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <AOIPolygonDrawer/>
      <MapBoundsTracker onBoundsChange={setmapBounds} />
      {shipData?.data && (<ShipMarkers shipdata={shipData.data} />)}
      {shipData?.data && (<CourseDirMarkers shipdata={shipData.data} />)}
      {aoiData?.data && (<RenderAOIs aoicoordsdata={aoiData.data} />)}
      {geofenceData?.data && (<RenderGeofences geofencecoordsdata={geofenceData.data} />)}
    </MapContainer>
    <NavigateToInputsButton />
    </>
  );
  
}

export default DrawAOIPage;