import "leaflet/dist/leaflet.css";
import './styles.css';
import { MapContainer, TileLayer, Marker, Popup, Rectangle } from 'react-leaflet';
import { Icon } from "leaflet";
import CursorIcon from "./cursor.png";
import { useEffect, useState } from "react";
import { ShipMarkers, CourseDirMarkers } from "./shipmarkers";
import { rectangleOverlay } from "./Polygon.js";
import {get_ships_past_day} from './utils.js';





function App() {

  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:3});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:20});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:100, time_within:3000});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, time_within:3000});
  // get_ships_past_day({lat_min:1.266477533544827, lat_max:1.2535264424975803, long_min:103.82335160632802, long_max:103.85594676548685});

  const [shipData, setShipData] = useState({});

  /* useEffect for API */

  useEffect(() => {
    get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685})
      .then(fetchdata => {
        if (fetchdata === null) {
          console.log("API did not return data");
        } else {
          setShipData(fetchdata);
        }
      })
    })



  /* useEffect for local JSON */

  // useEffect(() => {
  //   fetch("./data/shiptestlocations.json", {})
  //     .then(response => response.json())
  //     .then(fetchdata => {
  //       if (fetchdata === null) {
  //         console.log("API did not return data");
  //       } else {
  //         setShipData(fetchdata);
  //       }
  //     })
  //   }, [])


  console.log(shipData)
  

  if (Object.keys(shipData).length !== 0){
    return (
      <MapContainer center={[1.2595764399413216, 103.8335830126783]} zoom={15} scrollWheelZoom={true}>
        <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {CourseDirMarkers(shipData.data)}
        {ShipMarkers(shipData.data)}
        {rectangleOverlay(shipData.filters.bbox)}
      </MapContainer>
    );
  }
}

export default App;
