import { add_poly_geofence } from "./utils";

export default function GeofenceSidebar({
    drawing,
    setDrawing,
    coords,
    setCoords,
    name,
    setName,
    desc,
    setDesc
}) {

    const submitPolygon = async () => {

        if (coords.length < 3) {
            alert("Need at least 3 vertices");
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

            await add_poly_geofence({
                name,
                desc,
                coords: JSON.stringify(polygon)
            });

            alert("Geofence created");

            setCoords([]);
            setDrawing(false);

        } catch (err) {

            console.error(err);

        }
    };

    return (
        <div
            style={{
                width: "300px",
                padding: "20px",
                borderRight: "1px solid #ccc",
                background: "#fff",
                overflowY: "auto"
            }}
        >
            <h2>Geofence Drawing</h2>

            <button
                onClick={() =>
                    setDrawing(!drawing)
                }
            >
                {
                    drawing
                        ? "Stop Drawing"
                        : "Start Drawing"
                }
            </button>


            <div>
                Vertices: {coords.length}
            </div>

            <input
                placeholder="Geofence Name"
                value={name}
                onChange={(e) =>
                    setName(e.target.value)
                }
                style={{
                    width: "100%",
                    marginTop: "10px"
                }}
            />

            <textarea
                placeholder="Description"
                value={desc}
                onChange={(e) =>
                    setDesc(e.target.value)
                }
                style={{
                    width: "100%",
                    marginTop: "10px"
                }}
            />

            <button
                onClick={submitPolygon}
                style={{
                    marginTop: "10px"
                }}
            >
                Submit Geofence
            </button>

            <button
                onClick={() => setCoords([])}
                style={{
                    marginTop: "10px",
                    marginLeft: "10px"
                }}
            >
                Clear
            </button>
        </div>
    );
}