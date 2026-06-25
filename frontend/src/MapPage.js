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
import { NavigateToAlertHistoryButton, NavigateToAOIDrawButton, NavigateToGeofenceDrawButton, NavigateToInputsButton } from "./NavigateButtons.js";
import AOIPolygonDrawer from "./AOIPolygonDrawer";
import GeofencePolygonDrawer from "./GeofencePolygonDrawer.js";



function MapPage() {

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

  //HTML return
  return (
    <>
    <MapContainer center={[1.2595764399413216, 103.8335830126783]} zoom={14} scrollWheelZoom={true}>
      <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapBoundsTracker onBoundsChange={setmapBounds} />
      {shipData?.data && (<ShipMarkers shipdata={shipData.data} />)}
      {shipData?.data && (<CourseDirMarkers shipdata={shipData.data} />)}
      {aoiData?.data && (<RenderAOIs aoicoordsdata={aoiData.data} refreshAOIs={loadAOIs}/>)}
      {geofenceData?.data && (<RenderGeofences geofencecoordsdata={geofenceData.data} />)}
    </MapContainer>
    <NavigateToInputsButton />
    <NavigateToAOIDrawButton />
    <NavigateToGeofenceDrawButton />
    <NavigateToAlertHistoryButton />
    </>
  );
  
}

export default MapPage;





//DEPRECATED CODE
  // const [aoiCoordList, setaoiCoordList] = useState([
  //   {"lat_min":1.2535264424975803, "lat_max":1.266477533544827, "long_min":103.82335160632802, "long_max":103.85594676548685}
  // ]);

  // const [counter, setCounter] = useState(0);

  // const [shipDataArray, setShipDataArray] = useState([]);

  // function getAOIcoords(aoicoords) {
  //   setaoiCoordList([
  //     ...aoiCoordList,
  //     aoicoords
  //   ]);
  // }

  // function mapArrayToComponents(arrayofShipData) {
  //   const markers = 
  // }




  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:3});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:20});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:100, time_within:3000});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, time_within:3000});
  // get_ships_past_day({lat_min:1.266477533544827, lat_max:1.2535264424975803, long_min:103.82335160632802, long_max:103.85594676548685});


  // latmin: 1.2550417490810404, latmax: 1.2679667570273256 , longmin: 103.8882165259278 , longmax: 103.90781049237695

  
  

  /* useEffect for API */

  // useEffect(
  //   () => {
  //     for (let i = 0; i < aoiCoordList.length; i++) {
  //       get_ships_past_day(aoiCoordList[i])
  //       .then(fetchdata => {
  //         if (fetchdata === null) {
  //           console.log("API did not return data");
  //         } else {
  //           setShipData(fetchdata);
  //           console.log(shipData);
  //           console.log(shipDataArray);
  //           console.log(shipDataArray.length);
  //           console.log(aoiCoordList);
  //           let index = -1;
  //           index = shipDataArray.findIndex(x => x?.filters?.bbox == aoiCoordList[i]);
            
  //           if (index === -1) {
  //             setShipDataArray([
  //               ...shipDataArray,
  //               fetchdata
  //             ]);
  //           } else {
  //             const newDataArray = shipDataArray.map((c, p) => {
  //               if (p === index) {
  //                 return fetchdata;
  //               } else {
  //                 return c;
  //               }
  //             })
  //             setShipDataArray(newDataArray);
  //           }
  //         }
  //       })
  //     }
  //   }, [aoiCoordList]
  // )

  // useEffect(() => {
  //   get_ships_on_screen({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685})
  //     .then(fetchdata => {
  //       if (fetchdata === null) {
  //         console.log("API did not return data");
  //       } else {
  //         setshipData(fetchdata);
  //       }
  //     })
  //   }, [])


  /* useEffect for local JSON */

  // useEffect(() => {
  //   fetch("./data/shiptestlocations.json", {})
  //     .then(response => response.json())
  //     .then(fetchdata => {
  //       if (fetchdata === null) {
  //         console.log("API did not return data");
  //       } else {
  //         setshipData(fetchdata);
  //       }
  //     })
  //   }, [])

