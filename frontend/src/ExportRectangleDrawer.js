import { useEffect, useRef } from "react";
import { FeatureGroup } from "react-leaflet";
import { GeomanControls } from "react-leaflet-geoman-v2";

export default function ExportRectangleDrawer({
    bounds,
    setBounds
}) {
    const rectangleRef = useRef(null);

    const updateBounds = (layer) => {
        const b = layer.getBounds();

        setBounds({
            lat_min: b.getSouth(),
            lat_max: b.getNorth(),
            long_min: b.getWest(),
            long_max: b.getEast()
        });
    };

    const handleCreate = ({ layer }) => {

        if (rectangleRef.current) {
            rectangleRef.current.remove();
        }

        rectangleRef.current = layer;

        updateBounds(layer);

        layer.pm.enable();

    };

    const handleEdit = ({ layer }) => {
        updateBounds(layer);
    };

    const handleRemove = () => {
        rectangleRef.current = null;
        setBounds(null);
    };

    useEffect(() => {

        if (!bounds && rectangleRef.current) {

            rectangleRef.current.remove();
            rectangleRef.current = null;

        }

    }, [bounds]);

    return (
        <FeatureGroup>

            <GeomanControls
                options={{
                    position: "topright",

                    drawRectangle: true,

                    drawPolygon: false,
                    drawPolyline: false,
                    drawMarker: false,
                    drawCircle: false,
                    drawCircleMarker: false,
                    drawText: false,
                    cutPolygon: false,
                    rotateMode: false,
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
