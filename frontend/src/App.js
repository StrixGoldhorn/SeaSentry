import "leaflet/dist/leaflet.css";
import './styles.css';
import { MapContainer, TileLayer, Marker, Popup, } from 'react-leaflet';
import { Icon } from "leaflet";
import CursorIcon from "./cursor.png";
import { useEffect, useState } from "react";
import { ShipMarkers } from "./shipmarkers";






function App() {

  
  const [shipData, setShipData] = useState({});
  useEffect(() => {
    fetch("./data/shiptestlocations.json", {})
      .then(response => response.json())
      .then(fetchdata => {
        if (fetchdata === null) {
          console.log("API did not return data");
        } else {
          setShipData(fetchdata.data);
        }
      })
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
