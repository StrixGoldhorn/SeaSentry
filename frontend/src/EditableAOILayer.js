import { useEffect, useRef } from "react";
import { useMap, Polygon } from "react-leaflet";

export default function EditableAOILayer({
    coords,
    setCoords
}) {
    const ref = useRef();
    const map = useMap();
    useEffect(() => {
        if (!ref.current) return;
        const layer = ref.current;
        
        layer.pm.enable({
            allowSelfIntersection: false
        });

        function update() {
            setCoords(
                layer.getLatLngs()[0]
                    .map(p => [
                        p.lng,
                        p.lat
                    ])
            );

        }
        layer.on("pm:edit", update);
        layer.on("pm:dragend", update);
        layer.on("pm:rotateend", update);

        return () => {
            layer.off("pm:edit", update);
            layer.off("pm:dragend", update);
            layer.off("pm:rotateend", update);
            layer.pm.disable();
        };
    }, []);

    return (
        <Polygon
            ref={ref}
            positions={
                coords.map(
                    ([lng, lat]) => [lat, lng]
                )
            }

            pathOptions={{
                color: "red",
                weight: 4
            }}

        />

    );

}