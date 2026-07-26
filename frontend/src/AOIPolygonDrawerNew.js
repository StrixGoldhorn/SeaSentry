import { useEffect, useRef } from "react";
import { FeatureGroup } from "react-leaflet";
import { GeomanControls } from "react-leaflet-geoman-v2";

export default function AOIPolygonDrawerNew({
    coords,
    setCoords
}) {

    const polygonRef = useRef(null);

    const updateCoords = (layer) => {

        const latlngs = layer.getLatLngs()[0];

        setCoords(
            latlngs.map(({ lat, lng }) => [
                lng,
                lat
            ])
        );
    };

    const handleCreate = ({ layer }) => {

        if (polygonRef.current) {
            polygonRef.current.remove();
        }

        polygonRef.current = layer;

        updateCoords(layer);

        layer.pm.enable();

    };

    const handleEdit = ({ layer }) => {
        updateCoords(layer);
    };

    const handleRemove = () => {

        polygonRef.current = null;

        setCoords([]);

    };

    useEffect(() => {

        if (
            coords.length === 0 &&
            polygonRef.current
        ) {

            polygonRef.current.remove();

            polygonRef.current = null;

        }

    }, [coords]);

    return (

        <FeatureGroup>

            <GeomanControls

                options={{
                    position: "topright",

                    drawMarker: false,
                    drawCircle: false,
                    drawCircleMarker: false,
                    drawPolyline: false,
                    drawRectangle: false,
                    drawText: false,
                    removalMode: false
                }}

                globalOptions={{
                    continueDrawing: false
                }}

                onCreate={handleCreate}

                onEdit={handleEdit}

                onRemove={handleRemove}

            />

        </FeatureGroup>

    );

}