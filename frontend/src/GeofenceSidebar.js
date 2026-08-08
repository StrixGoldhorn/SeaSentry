import { add_poly_geofence } from "./utils";
import { useSnackbar } from "./SnackbarContext";

export default function GeofenceSidebar({
    coords,
    setCoords,
    name,
    setName,
    desc,
    setDesc
}) {
    const { showSnackbar } = useSnackbar();

    const submitPolygon = async () => {

        if (coords.length < 3) {
            showSnackbar("Please draw a Geofence first.", "error");
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

            const res = await add_poly_geofence({
                name,
                desc,
                coords: JSON.stringify(polygon)
            });

            if (res?.error) {
                showSnackbar(`Failed to create Geofence: ${res.error}`);
                return;
            } else if (res?.status && res.status >= 400) {
                showSnackbar(`Failed to create Geofence: Status ${res.status}`);
                return;
            }

            showSnackbar("Geofence created", "success");

            setCoords([]);
            setName("");
            setDesc("");

        } catch (err) {

            console.error(err);
            showSnackbar(`Failed to create Geofence: ${err}`);

        }

    };

    return (

        <div
            style={{
                width: 300,
                padding: 20,
                background: "white"
            }}
        >

            <h2>Draw Geofence</h2>

            <p>
                <strong>Use Polygon tools on the right of this box.</strong>
                
            </p>

            <p>
                Vertices: {coords.length}
            </p>

            <input
                placeholder="Geofence Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ width: "100%" }}
            />

            <textarea
                placeholder="Description"
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                style={{
                    width: "100%",
                    marginTop: 10
                }}
            />

            <button
                onClick={submitPolygon}
                style={{ marginTop: 10 }}
            >
                Submit Geofence
            </button>

            <button
                onClick={() => setCoords([])}
                style={{
                    marginTop: 10,
                    marginLeft: 10
                }}
            >
                Clear
            </button>

        </div>

    );

}