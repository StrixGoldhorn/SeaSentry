import { useState } from "react";
import { Polygon, useMapEvents } from "react-leaflet";
import { add_poly_AOI } from "./utils";

function AOIClickHandler({ enabled, onPointAdd }) {
    useMapEvents({
        click(e) {
            if (!enabled) return;

            onPointAdd([
                e.latlng.lng,
                e.latlng.lat
            ]);
        }
    });

    return null;
}

export default function AOIPolygonDrawer() {

    const [drawing, setDrawing] = useState(false);

    const [name, setName] = useState("");

    const [desc, setDesc] = useState("");

    const [coords, setCoords] = useState([]);

    const addPoint = (point) => {
        setCoords(prev => [...prev, point]);
    };

    const clearPolygon = () => {
        setCoords([]);
    };

    const submitPolygon = async () => {

        if (coords.length < 3) {
            alert("Polygon requires at least 3 points");
            return;
        }

        let polygon = [...coords];

        const first = polygon[0];
        const last = polygon[polygon.length - 1];

        if (
            first[0] !== last[0] ||
            first[1] !== last[1]
        ) {
            polygon.push(first);
        }

        try {

            await add_poly_AOI({
                name,
                desc: desc || null,
                coords: JSON.stringify(polygon)
            });

            alert("AOI created");

            setCoords([]);
            setDrawing(false);

        } catch (err) {

            console.error(err);
            alert("Failed to create AOI");

        }
    };

    return (
        <>
            <div
                style={{
                    position: "absolute",
                    top: 10,
                    left: 60,
                    zIndex: 1000,
                    background: "white",
                    padding: "10px",
                    borderRadius: "8px"
                }}
            >

                <button
                    onClick={() => setDrawing(prev => !prev)}
                >
                    {drawing
                        ? "Cancel AOI Drawing"
                        : "Draw AOI"}
                </button>

                {drawing && (
                    <>
                        <br />

                        <input
                            placeholder="AOI Name"
                            value={name}
                            onChange={(e) =>
                                setName(e.target.value)
                            }
                        />

                        <br />

                        <input
                            placeholder="Description"
                            value={desc}
                            onChange={(e) =>
                                setDesc(e.target.value)
                            }
                        />

                        <br />

                        <button onClick={submitPolygon}>
                            Submit AOI
                        </button>

                        <button onClick={clearPolygon}>
                            Clear
                        </button>
                    </>
                )}
            </div>

            <AOIClickHandler
                enabled={drawing}
                onPointAdd={addPoint}
            />

            {coords.length > 1 && (
                <Polygon
                    positions={coords.map(
                        ([lng, lat]) => [lat, lng]
                    )}
                />
            )}
        </>
    );
}