import { Polygon, Popup } from "react-leaflet";

export function PolygonOverlay({
    item,
    color = "black",

    polygonField,
    idField,
    nameField,
    descriptionField,
    timestampField,

    deleteFunction,
    refreshFunction,
    onEdit,
    editing,

    editLabel = "Edit",
    deleteLabel = "Delete"
}) {

    const polyOptions = {
        color,
        weight: 3,
        opacity: 0.3,
        fillColor: color,
        fillOpacity: 0.03,
        pmIgnore: true
    };

    const polyBounds =
        item[polygonField].map(
            ([lng, lat]) => [lat, lng]
        );

    async function handleDelete() {

        const confirmed = window.confirm(
            `Delete "${item[nameField]}"?`
        );

        if (!confirmed) {
            return;
        }

        try {

            await deleteFunction({
                id: item[idField],
                name: item[nameField]
            });

            if (refreshFunction) {
                refreshFunction();
            }

        } catch (err) {

            console.error(err);

            alert("Delete failed");

        }
    }

    return (
        <Polygon
            positions={polyBounds}
            pathOptions={polyOptions}
            interactive={!editing}
        >
            <Popup autoPan={false}>

                <div style={{ minWidth: "250px" }}>

                    <h3>
                        {item[nameField]}
                    </h3>

                    <hr />

                    <p>
                        <strong>ID:</strong>{" "}
                        {item[idField]}
                    </p>

                    <p>
                        <strong>Description:</strong>
                        <br />
                        {
                            item[descriptionField] ||
                            "No description"
                        }
                    </p>

                    <p>
                        <strong>Created:</strong>
                        <br />
                        {
                            item[timestampField]
                                ? new Date(
                                    item[timestampField]
                                ).toLocaleString()
                                : "Unknown"
                        }
                    </p>

                    <p>
                        <strong>Vertices:</strong>{" "}
                        {item[polygonField].length}
                    </p>

                    

                    <button
                        style={{
                            width: "100%",
                            marginTop: 10
                        }}
                        onClick={() => onEdit(item)}
                    >
                        {editLabel}
                    </button>

                    <button
                        style={{
                            width: "100%",
                            marginTop: 10
                        }}
                        onClick={handleDelete}
                    >
                        {deleteLabel}
                    </button>

                </div>

            </Popup>
        </Polygon>
    );
}






//DEPRECATED
// export function RectangleOverlay ({ bbox, color }) {

//     const rectOptions = {
//         color: `${color}`,
//         weight: 3,
//         opacity: 0.3,
//         fillColor: `${color}`,
//         fillOpacity: 0.03
//     }

//     const rectBounds = [
//         [bbox.lat_min, bbox.long_min],
//         [bbox.lat_max, bbox.long_max]
//     ]

//     return (
//         <Rectangle bounds={rectBounds} pathOptions={rectOptions} />
//     )
// }
