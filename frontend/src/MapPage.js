import "leaflet/dist/leaflet.css";
import './styles.css';
import { MapContainer, TileLayer, LayerGroup, Marker, Popup, Rectangle, Polygon,
     useMap, useMapEvent, useMapEvents, LayersControl, WMSTileLayer, ZoomControl, CircleMarker } from 'react-leaflet';
import { Icon } from "leaflet";
import { useEffect, useState } from "react";
import { ShipMarkers, CourseDirMarkers } from "./shipmarkers.js";
import * as utils from './utils.js';
import { MapBoundsTracker, MapStateSaver, getMapCenter, getMapZoom } from "./screenbounds.js";
import { RenderAOIs, RenderGeofences } from "./Boundsrenders.js";
import EditableAOILayer from "./EditableAOILayer.js";
import ThinSidebar from "./ThinSidebar.js";
import SlidingSidebar from "./SlidingSidebar.js";
import AOIPolygonDrawerNew from "./AOIPolygonDrawerNew.js";
import GeofencePolygonDrawerNew from "./GeofencePolygonDrawerNew.js";
import CopernicusImageryLayerControl from "./CopernicusImageryLayerControl.js";
import ExportRectangleDrawer from "./ExportRectangleDrawer";
import Cluster from 'react-leaflet-cluster';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.Default.css';
import VesselHeatmap from "./VesselHeatmap";
import { useSnackbar } from "./SnackbarContext";

const SHIP_TYPES = [
  "Cargo",
  "Fishing",
  "High Speed Craft",
  "Law Enforcement",
  "Medical Transport",
  "Military",
  "Passenger",
  "Pleasure Craft",
  "Sailing",
  "SAR",
  "Tanker",
  "Tug"
];

function MapPage() {

  //useStates
  const [shipData, setshipData] = useState({});
  const [aoiData, setaoiData] = useState({});
  const [geofenceData, setgeofenceData] = useState({});
  const [exportBounds, setExportBounds] = useState(null);
  const [mapBounds, setmapBounds] = useState(null);

  const [selectedShiptype, setSelectedShiptype] = useState("");
  const [appliedShiptype, setAppliedShiptype] = useState("");

  const [editingItem, setEditingItem] = useState(null);
  const [editingType, setEditingType] = useState(null);
  const [editedCoords, setEditedCoords] = useState([]);
  const [editing, setEditing] = useState(false);

  const [editedName, setEditedName] = useState("");
  const [editedDescription, setEditedDescription] = useState("");

  const [sidebarMode, setSidebarMode] = useState(null);

  const [drawing, setDrawing] = useState(false);

  const [coords, setCoords] = useState([]);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");

  const [instanceId, setInstanceId] = useState("");
  const [selectedLayer, setSelectedLayer] = useState("none");

  const [showHeatmap, setShowHeatmap] = useState(false);


  const [alertVessels, setAlertVessels] = useState(new Map());
  const [refreshKey, setRefreshKey] = useState(0);
  const { showSnackbar } = useSnackbar();
  
  const [currentZoom, setCurrentZoom] = useState(getMapZoom() || 14);
  function ZoomTracker({ onZoomChange }) {
    useMapEvents({
      zoomend: (e) => {
        onZoomChange(e.target.getZoom());
    console.log(e.target.getZoom());
      },
    });
    return null;
  }

  const openAOI = () => {
      setSidebarMode("aoi");
      setDrawing(true);
  };

  const openGeofence = () => {
      setSidebarMode("geofence");
      setDrawing(true);
  };

  const closeSidebar = () => {
      setSidebarMode(null);
      setDrawing(false);

      setCoords([]);
      setName("");
      setDesc("");
  };

  const handleSidebarSelect = (mode) => {
      // Clicking the currently open tool closes it
      if (sidebarMode === mode) {
          closeSidebar();
          return;
      }

      // Otherwise switch to the selected tool
      setSidebarMode(mode);
      setDrawing(mode === "aoi" || mode === "geofence");

      // Optional: clear previous drawing
      setCoords([]);
      setName("");
      setDesc("");
  };

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
          let res;
          if (editingType === "aoi") {
              res = await utils.update_AOI({
                  aoi_id:
                      editingItem.area_of_interest_id,
                  name: editedName,
                  desc: editedDescription,
                  coords:
                      editedCoords
              });
              if (res?.error) {
                  showSnackbar(`Failed to update AOI: ${res.error}`);
                  return;
              } else if (res?.status && res.status >= 400) {
                  showSnackbar(`Failed to update AOI: Status ${res.status}`);
                  return;
              }
              loadAOIs();
          }

          if (editingType === "geofence") {
              res = await utils.update_geofence({
                  geofence_id:
                      editingItem.geofence_id,
                  name: editedName,
                  desc: editedDescription,
                  coords:
                      editedCoords
              });
              if (res?.error) {
                  showSnackbar(`Failed to update geofence: ${res.error}`);
                  return;
              } else if (res?.status && res.status >= 400) {
                  showSnackbar(`Failed to update geofence: Status ${res.status}`);
                  return;
              }
              loadGeofences();
          }
          cancelEditing();
      }

      catch (err) {
          console.error(err);
          showSnackbar(`Failed to update: ${err}`);
      }
  }


  //useEffects
  useEffect(() => {
      if (!mapBounds) return;

    const timeoutId = setTimeout(() => {
      const filterParams = { ...mapBounds };
      if (appliedShiptype) {
        filterParams.shiptype = appliedShiptype;
      }

      utils.get_ships_on_screen(filterParams)
        .then(fetchdata => {
          if (fetchdata) {
            setshipData(fetchdata);
          }
        });
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [mapBounds, appliedShiptype]);

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

  useEffect(() => {
        const savedId = localStorage.getItem("sentinelHubInstanceId");
        if (savedId) {
            setInstanceId(savedId);
        }
    }, []);

  const fetchAlerts = () => {
      utils.get_all_alert_history({ limit: 500 }).then(fetchdata => {
          let alertsArray = [];
          if (fetchdata?.data) {
              alertsArray = fetchdata.data;
          } else if (Array.isArray(fetchdata)) {
              alertsArray = fetchdata;
          }
          
          const unread = alertsArray.filter(a => !a.alert_history_read);
          const mmsis = new Map();
          
          unread.forEach(alert => {
              if (alert.alert_history_context?.matched_vessels) {
                  alert.alert_history_context.matched_vessels.forEach(v => {
                      if (v.mmsi) {
                          const mmsiStr = String(v.mmsi);
                          if (!mmsis.has(mmsiStr)) {
                              mmsis.set(mmsiStr, []);
                          }
                          mmsis.get(mmsiStr).push(alert);
                      }
                  });
              }
          });
          
          setAlertVessels(mmsis);
      }).catch(err => console.error("Error fetching alert vessels:", err));
  };

  useEffect(() => {
      fetchAlerts();
      const interval = setInterval(fetchAlerts, 15000);
      return () => clearInterval(interval);
  }, []);

  const markAlertAsRead = async (alert_history_id) => {
      try {
          await utils.mark_alert_read({ alert_history_id });
          showSnackbar("Alert marked as read", "success");
          fetchAlerts();
      } catch (err) {
          console.error(err);
          showSnackbar(`Error marking alert as read: ${err}`);
      }
  };

  const markAllAlertsForShipAsRead = async (alerts) => {
      try {
          await Promise.all(alerts.map(a => utils.mark_alert_read({ alert_history_id: a.alert_history_id })));
          showSnackbar("All alerts marked as read for vessel", "success");
          fetchAlerts();
      } catch (err) {
          console.error(err);
          showSnackbar(`Error marking alerts as read: ${err}`);
      }
  };

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

  const handleApplyFilter = () => {
    setAppliedShiptype(selectedShiptype);
  };

  const handleClearFilter = () => {
    setSelectedShiptype("");
    setAppliedShiptype("");
  };

  const getClusterRadius = (zoom) => {
    if (zoom >= 12) return 60;
    if (zoom >= 10) return 100;
    if (zoom >= 8) return 200;
    return 500;
  };

  let initialCenter = getMapCenter();
  let initialZoom = getMapZoom();

  //HTML return
  return (
    <>
    <ThinSidebar onSelect={handleSidebarSelect} selectedMode={sidebarMode} />

    <SlidingSidebar
        open={sidebarMode !== null}
        mode={sidebarMode}
        close={closeSidebar}

        drawing={drawing}
        setDrawing={setDrawing}

        coords={coords}
        setCoords={setCoords}

        name={name}
        setName={setName}

        desc={desc}
        setDesc={setDesc}

        instanceId={instanceId}
        setInstanceId={setInstanceId}
        selectedLayer={selectedLayer}
        setSelectedLayer={setSelectedLayer}

        bounds={exportBounds}
        setBounds={setExportBounds}
        
        selectedShiptype={selectedShiptype}
        setSelectedShiptype={setSelectedShiptype}
        appliedShiptype={appliedShiptype}
        setAppliedShiptype={setAppliedShiptype}
    />
    <MapContainer center={initialCenter} zoom={initialZoom} maxZoom={20} scrollWheelZoom={true} zoomControl={false}>

      <MapStateSaver/>
      <HeatmapOverlayWatcher onToggle={setShowHeatmap} />
      <ZoomTracker onZoomChange={setCurrentZoom} />
      <ZoomControl position="topright" />

     <LayersControl position="topright">

        <LayersControl.BaseLayer checked name="OpenStreetMap">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="OpenStreetMap"
            zIndex={1}
          />
        </LayersControl.BaseLayer>

        <LayersControl.BaseLayer name="ESRI World Imagery">
          <TileLayer
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.jpg"
            attribution="ESRI"
            zIndex={1}
          />
        </LayersControl.BaseLayer>

        <LayersControl.BaseLayer name="Google Satellite">
          <TileLayer
            url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
            attribution="Google"
            zIndex={1}
          />
        </LayersControl.BaseLayer>

        <LayersControl.Overlay name="Nautical Chart (OpenSeaMap)">
          <TileLayer
            url="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
            opacity={1}
            updateWhenIdle={true}
            attribution="OpenSeaMap"
            zIndex={10}
          />
        </LayersControl.Overlay>

        <LayersControl.Overlay name="Vessel Heatmap">
            <LayerGroup />
        </LayersControl.Overlay>

        <LayersControl.Overlay checked name="Vessel Markers">
            <LayerGroup name="Vessel Markers">
                {!drawing && !editing && (
                    <Cluster
                        chunkedLoading
                        showCoverageOnHover={false}
                        maxClusterRadius={getClusterRadius(currentZoom)}
                        disableClusteringAtZoom={14}
                    >
                        {shipData?.data && (
                            <ShipMarkers 
                                shipdata={shipData.data} 
                                alertVessels={alertVessels}
                                onMarkAlertRead={markAlertAsRead}
                            />
                        )}
                        {shipData?.data && (
                            <CourseDirMarkers shipdata={shipData.data} />
                        )}
                    </Cluster>
                )}
            </LayerGroup>
        </LayersControl.Overlay>
      
        <LayersControl.Overlay checked name="Alert Highlights">
            <LayerGroup name="Alert Highlights">
                {!drawing && !editing && shipData?.data && shipData.data
                    .filter(ship => alertVessels.has(String(ship.mmsi)))
                    .map(ship => {
                        const lat = ship.lat ?? ship.latitude;
                        const lng = ship.long ?? ship.longitude ?? ship.lng;
                        if (lat == null || lng == null) return null;
                        const alertsForShip = alertVessels.get(String(ship.mmsi));
                        
                        return (
                            <CircleMarker
                                key={`alert-${ship.mmsi}`}
                                center={[lat, lng]}
                                radius={25}
                                pathOptions={{
                                    color: "#ff0000",
                                    fillColor: "#ff0000",
                                    fillOpacity: 0.3,
                                    weight: 3,
                                    dashArray: "4, 6",
                                }}
                            >
                                <Popup autoPan={false}>
                                    <div style={{ minWidth: "250px" }}>
                                        <h3 style={{ color: "#cc0000" }}>
                                            Alerts: {ship.ship_name || ship.mmsi}
                                        </h3>
                                        {alertsForShip.length > 1 && (
                                            <div style={{ marginBottom: "10px", marginTop: "5px" }}>
                                                <button 
                                                    style={{ margin: "0px", width: "100%" }}
                                                    onClick={() => markAllAlertsForShipAsRead(alertsForShip)}
                                                >
                                                    Acknowledge All
                                                </button>
                                            </div>
                                        )}
                                        <hr />
                                        <div style={{ maxHeight: "400px", overflowY: "auto", paddingRight: "5px" }}>
                                            {alertsForShip.map((alert, index) => (
                                                <div key={alert.alert_history_id}>
                                                    <p>
                                                        <strong>Rule:</strong>{" "}
                                                        {alert.alert_history_context?.rule_name}
                                                    </p>
                                                    <p>
                                                        <strong>Triggered:</strong><br />
                                                        {new Date(alert.alert_history_timestamp).toLocaleString()}
                                                    </p>
                                                    <div style={{
                                                        display: 'grid',
                                                        gridTemplateColumns: '1fr',
                                                        padding: '0px',
                                                        marginTop: '10px',
                                                        marginBottom: '10px'
                                                    }}>
                                                        <button 
                                                            style={{ margin: "0px" }}
                                                            onClick={() => markAlertAsRead(alert.alert_history_id)}
                                                        >
                                                            Mark as Read
                                                        </button>
                                                    </div>
                                                    {index < alertsForShip.length - 1 && <hr />}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </Popup>
                            </CircleMarker>
                        );
                    })
                }
            </LayerGroup>
        </LayersControl.Overlay>

      </LayersControl>

      <MapBoundsTracker onBoundsChange={setmapBounds} />

      {showHeatmap && shipData?.data && (
          <VesselHeatmap shipdata={shipData.data} />
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

    {instanceId && selectedLayer === "sentinel2" && (
        <WMSTileLayer
            url={`https://sh.dataspace.copernicus.eu/ogc/wms/${instanceId}`}
            layers="TRUE_S2L2A"
            format="image/png"
            transparent={true}
            version="1.3.0"
            attribution="Sentinel-2 imagery"
            zIndex={5}
        />
    )}

    {instanceId && selectedLayer === "sentinel1" && (
        <WMSTileLayer
            url={`https://sh.dataspace.copernicus.eu/ogc/wms/${instanceId}`}
            layers="SAR_VV_VH"
            format="image/png"
            transparent={true}
            version="1.3.0"
            attribution="Sentinel-1 imagery"
            zIndex={5}
        />
    )}

    {sidebarMode === "aoi" && (
        <AOIPolygonDrawerNew
            drawing
            coords={coords}
            setCoords={setCoords}
        />
    )}

    {sidebarMode === "geofence" && (
        <GeofencePolygonDrawerNew
            drawing
            coords={coords}
            setCoords={setCoords}
        />
    )}

    {sidebarMode === "export" && (
        <ExportRectangleDrawer
            bounds={exportBounds}
            setBounds={setExportBounds}
        />
    )}

    </MapContainer>
    {editing && (
      <div
          style={{
              position: "absolute",
              top: 50,
              right: 10,
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
    </>
  );
}

function HeatmapOverlayWatcher({ onToggle }) {
    const map = useMap();

    useEffect(() => {
        const handleAdd = (e) => {
            if (e.name === "Vessel Heatmap") {
                onToggle(true);
            }
        };

        const handleRemove = (e) => {
            if (e.name === "Vessel Heatmap") {
                onToggle(false);
            }
        };

        map.on("overlayadd", handleAdd);
        map.on("overlayremove", handleRemove);

        return () => {
            map.off("overlayadd", handleAdd);
            map.off("overlayremove", handleRemove);
        };
    }, [map, onToggle]);

    return null;
}


export default MapPage;
