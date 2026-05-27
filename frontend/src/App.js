import "leaflet/dist/leaflet.css";
import './styles.css';
import { MapContainer, TileLayer, Marker, Popup, } from 'react-leaflet';
import { Icon } from "leaflet";
import CursorIcon from "./cursor.png";
import { useEffect, useState } from "react";
import { ShipMarkers } from "./shipmarkers";

import {get_ships_past_day} from './utils.js'




function App() {

  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:3});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:20});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, limit:100, time_within:3000});
  // get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685, time_within:3000});
  // get_ships_past_day({lat_min:1.266477533544827, lat_max:1.2535264424975803, long_min:103.82335160632802, long_max:103.85594676548685});

  const [shipData, setShipData] = useState({});
  useEffect(() => {
    get_ships_past_day({lat_min:1.2535264424975803, lat_max:1.266477533544827, long_min:103.82335160632802, long_max:103.85594676548685})
      .then(fetchdata => {
        if (fetchdata === null) {
          console.log("API did not return data");
        } else {
          setShipData(fetchdata.data);
        }
      })
  // }
  // useEffect(() => {
  //   fetch("./data/shiptestlocations.json", {})
  //     .then(response => response.json())
  //     .then(fetchdata => {
  //       if (fetchdata === null) {
  //         console.log("API did not return data");
  //       } else {
  //         setShipData(fetchdata.data);
  //       }
  //     })
  }, [])
  
  return (
    <MapContainer center={[51.505, -0.09]} zoom={1} scrollWheelZoom={true}>
      <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {
        ShipMarkers(shipData)
      }
    </MapContainer>
  );
}

export default App;
