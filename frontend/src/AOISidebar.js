import { add_poly_AOI } from "./utils";

export default function AOISidebar({
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

            await add_poly_AOI({
                name,
                desc,
                coords: JSON.stringify(polygon)
            });

            alert("AOI created");

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
            <h2>AOI Drawing</h2>

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

            <hr />

            <div>
                Vertices: {coords.length}
            </div>

            <input
                placeholder="AOI Name"
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
                Submit AOI
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