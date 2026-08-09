import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";

function VesselHeatmap({ shipdata }) {
    const map = useMap();

    useEffect(() => {
        if (!Array.isArray(shipdata)) return;

        const points = shipdata
            .filter(
                ship =>
                    ship.latitude != null &&
                    ship.longitude != null
            )
            .map(ship => [
                ship.latitude,
                ship.longitude,
                1 // intensity
            ]);

        const heatLayer = L.heatLayer(points, {
            radius: 25,
            blur: 20,
            maxZoom: 17,
            minOpacity: 0.35,
            gradient: {
                0.2: "#0000ff",
                0.4: "#00ffff",
                0.6: "#00ff00",
                0.8: "#ffff00",
                1.0: "#ff0000"
            }
        });

        heatLayer.addTo(map);

        return () => {
            map.removeLayer(heatLayer);
        };
    }, [map, shipdata]);

    return null;
}

export default VesselHeatmap;