import { useState } from "react";

import {
    Polygon,
    Polyline,
    CircleMarker,
    useMapEvents
} from "react-leaflet";

function AOIClickHandler({
    drawing,
    onPointAdd,
    onMouseMove
}) {

    useMapEvents({

        click(e) {

            if (!drawing) return;

            onPointAdd([
                e.latlng.lng,
                e.latlng.lat
            ]);
        },

        mousemove(e) {

            if (!drawing) return;

            onMouseMove([
                e.latlng.lng,
                e.latlng.lat
            ]);
        }

    });

    return null;
}

export default function AOIPolygonDrawerNew({
    drawing,
    coords,
    setCoords
}) {

    const [mousePos, setMousePos] =
        useState(null);

    const previewCoords =
        drawing &&
        mousePos &&
        coords.length > 0
            ? [...coords, mousePos]
            : coords;

    return (
        <>
            <AOIClickHandler
                drawing={drawing}
                onPointAdd={(point) =>
                    setCoords(prev => [
                        ...prev,
                        point
                    ])
                }
                onMouseMove={setMousePos}
            />

            {coords.map(
                ([lng, lat], index) => (
                    <CircleMarker
                        key={index}
                        center={[lat, lng]}
                        radius={6}
                    />
                )
            )}

            {drawing &&
                mousePos &&
                coords.length > 0 && (

                <Polyline
                    positions={[
                        [
                            coords[
                                coords.length - 1
                            ][1],
                            coords[
                                coords.length - 1
                            ][0]
                        ],
                        [
                            mousePos[1],
                            mousePos[0]
                        ]
                    ]}
                />

            )}

            {
                drawing &&
                mousePos && (
                    <CircleMarker
                        center={[
                            mousePos[1],
                            mousePos[0]
                        ]}
                        radius={6}
                        weight={2}
                        opacity={0.7}
                        fillOpacity={0.5}
                    />
                )
            }

            {previewCoords.length > 1 && (
                <Polygon
                    positions={
                        previewCoords.map(
                            ([lng, lat]) => [
                                lat,
                                lng
                            ]
                        )
                    }
                />
            )}
        </>
    );
}