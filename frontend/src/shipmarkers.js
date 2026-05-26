import { Icon } from "leaflet";
import { Marker } from "react-leaflet";
import CursorIcon from "./cursor.png";

const customIcon = new Icon({
  iconUrl: CursorIcon,
  iconSize: [38, 38]
})

export function ShipMarkers(shipdata) {
    if (shipdata instanceof Array) {
        return(shipdata.map(ship => (
                  <Marker position = {[ship.latitude, ship.longitude]} icon = {customIcon}>
                  </Marker>)))
    } else {
        return
    }
}