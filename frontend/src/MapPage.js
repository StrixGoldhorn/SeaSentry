import "leaflet/dist/leaflet.css";
import './styles.css';
import { MapContainer, TileLayer, Marker, Popup, Rectangle, Polygon, useMapEvent, useMapEvents } from 'react-leaflet';
import { Icon } from "leaflet";
import CursorIcon from "./cursor.png";
import { useEffect, useState } from "react";
import { ShipMarkers, CourseDirMarkers } from "./shipmarkers.js";
import * as utils from './utils.js';
import { MapBoundsTracker } from "./screenbounds.js";
import { RenderAOIs, RenderGeofences } from "./Boundsrenders.js";
import EditableAOILayer from "./EditableAOILayer.js";
import { NavigateToUnreadAlertHistoryButton, NavigateToAOIDrawButton, NavigateToGeofenceDrawButton, NavigateToInputsButton, NavigateToVesselsButton } from "./NavigateButtons.js";




function MapPage() {

  //useStates
  const [shipData, setshipData] = useState({});
  const [aoiData, setaoiData] = useState({});
  const [geofenceData, setgeofenceData] = useState({});
  const [mapBounds, setmapBounds] = useState({lat_min:0, lat_max:0, long_min:0, long_max:0});

  const [editingItem, setEditingItem] = useState(null);
  const [editingType, setEditingType] = useState(null);
  const [editedCoords, setEditedCoords] = useState([]);
  const [editing, setEditing] = useState(false);

  const [editedName, setEditedName] = useState("");
  const [editedDescription, setEditedDescription] = useState("");

  const [refreshKey, setRefreshKey] = useState(0);

  function startEditing(item, type) {

      setEditingItem(item);
      setEditingType(type);

      if (type === "aoi") {

          setEditedCoords(item.area_of_interest_polygon);
          setEditedName(item.area_of_interest_name);
          setEditedDescription(
              item.area_of_interest_description ?? ""
          );

      } else {

          setEditedCoords(item.geofence_polygon);
          setEditedName(item.geofence_name);
          setEditedDescription(
              item.geofence_description ?? ""
          );

      }

      setEditing(true);

  }

  function cancelEditing() {

      setEditing(false);

      setEditingItem(null);
      setEditingType(null);

      setEditedCoords([]);
      setEditedName("");
      setEditedDescription("");

      setRefreshKey(prev => prev + 1);

  }

  async function finishEditing() {
      try {
          if (editingType === "aoi") {
              await utils.update_AOI({
                  aoi_id:
                      editingItem.area_of_interest_id,
                  name: editedName,
                  desc: editedDescription,
                  coords:
                      editedCoords
              });
              loadAOIs();
          }

          if (editingType === "geofence") {
              await utils.update_geofence({
                  geofence_id:
                      editingItem.geofence_id,
                  name: editedName,
                  desc: editedDescription,
                  coords:
                      editedCoords
              });
              loadGeofences();
          }
          cancelEditing();
      }

      catch (err) {
          console.error(err);
          alert("Failed to update.");
      }
  }


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
      loadAOIs();
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


  const loadAOIs = () => {
    utils.get_all_AOI()
    .then(fetchdata => {
      if (fetchdata === null) {
        console.log("API did not return data");
      } else {
        setaoiData(fetchdata);
      }
    })
  }

  const loadGeofences = () => {
    utils.get_all_geofences()
    .then(fetchdata => {
      if (fetchdata === null) {
        console.log("API did not return data");
      } else {
        setgeofenceData(fetchdata);
      }
    })
  }


  //HTML return
  return (
    <>
    <MapContainer center={[1.2595764399413216, 103.8335830126783]} zoom={14} scrollWheelZoom={true}>
      <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapBoundsTracker onBoundsChange={setmapBounds} />
      {!editing && shipData?.data && (
          <ShipMarkers shipdata={shipData.data} />
      )}

      {!editing && shipData?.data && (
          <CourseDirMarkers shipdata={shipData.data} />
      )}

      {aoiData?.data && (<RenderAOIs 
      aoicoordsdata={aoiData.data}
      refreshAOIs={loadAOIs}
      editing={editing}
      onEdit={(item) => startEditing(item, "aoi")}
      />)}

      {geofenceData?.data && (<RenderGeofences 
      geofencecoordsdata={geofenceData.data}
      refreshGeofences={loadGeofences}
      editing={editing}
      onEdit={(item) => startEditing(item, "geofence")}
      />)}

      {editingItem && (
        <EditableAOILayer
        key={refreshKey}
        coords={editedCoords}
        setCoords={setEditedCoords}/>)}

    </MapContainer>
    {editing && (
      <div
          style={{
              position: "absolute",
              top: 20,
              right: 20,
              zIndex: 1000,
              background: "white",
              padding: 20,
              borderRadius: 8,
              boxShadow: "0 2px 8px rgba(0,0,0,.3)",
              width: 300
          }}
      >

          <h3>
              Editing {editingType === "aoi" ? "AOI" : "Geofence"}
          </h3>

          <label>Name</label>

          <input
              value={editedName}
              onChange={(e) =>
                  setEditedName(e.target.value)
              }
              style={{
                  width: "100%",
                  marginBottom: 12
              }}
          />

          <label>Description</label>

          <textarea
              rows={4}
              value={editedDescription}
              onChange={(e) =>
                  setEditedDescription(e.target.value)
              }
              style={{
                  width: "100%",
                  marginBottom: 12
              }}
          />

          <p>
              Vertices: {editedCoords.length}
          </p>

          <button
              onClick={finishEditing}
              style={{ width: "100%" }}
          >
              Save Changes
          </button>

          <button
              onClick={cancelEditing}
              style={{
                  width: "100%",
                  marginTop: 10
              }}
          >
              Cancel
          </button>

      </div>
      )}

    <NavigateToInputsButton />
    <NavigateToAOIDrawButton />
    <NavigateToGeofenceDrawButton />
    <NavigateToUnreadAlertHistoryButton />
    <NavigateToVesselsButton />
    </>
  );
}

export default MapPage;



