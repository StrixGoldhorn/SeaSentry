import { Polygon, Popup } from "react-leaflet";
import { useSnackbar } from "./SnackbarContext";

export function PolygonOverlay({
    item,
    color = "black",
    zIndexOffset = 0,

    polygonField,
    idField,
    nameField,
    descriptionField,
    timestampField,

    deleteFunction,
    scrapeFunction,
    refreshFunction,
    onEdit,
    editing,

    editLabel = "Edit",
    deleteLabel = "Delete",
    scrapeLabel = "Scrape"
}) {
    const { showSnackbar } = useSnackbar();

    const polyOptions = {
        color,
        weight: 3,
        opacity: 0.3,
        fillColor: color,
        fillOpacity: 0.03,
        pmIgnore: true,
        zIndexOffset
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

            const res = await deleteFunction({
                id: item[idField],
                name: item[nameField]
            });

            if (res?.error) {
                showSnackbar(`Delete failed: ${res.error}`);
                return;
            } else if (res?.status && res.status >= 400) {
                showSnackbar(`Delete failed: Status ${res.status}`);
                return;
            }

            if (refreshFunction) {
                refreshFunction();
            }

        } catch (err) {

            console.error(err);

            showSnackbar(`Delete failed: ${err}`);

        }
    }

    async function handleScrape() {

        const confirmed = window.confirm(
            `Confirm scrape "${item[nameField]}"?\nDo not spam this too often, even with different AOIs.`
        );

        if (!confirmed) {
            return;
        }

        try {

            const res = await scrapeFunction({
                id: item[idField]
            });

            if (res?.error) {
                showSnackbar(`Scrape failed: ${res.error}`);
                return;
            } else if (res?.status && res.status >= 400) {
                showSnackbar(`Scrape failed: Status ${res.status}`);
                return;
            }

            if (refreshFunction) {
                refreshFunction();
            }

            showSnackbar("Scrape successful", "success");

        } catch (err) {

            console.error(err);

            showSnackbar(`Force scrape failed: ${err}`);

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

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '10px',
                        padding: '0px'
                    }}>
                        {scrapeFunction && (
                            <button
                                style={{
                                    gridColumn: 'span 2',
                                    margin: '0px',

                                }}
                                onClick={handleScrape}
                            >
                                {scrapeLabel}
                            </button>
                        )}

                        <button
                            style={{
                                margin: '0px',
                            }}
                            onClick={() => onEdit(item)}
                        >
                            {editLabel}
                        </button>

                        <button
                            style={{
                                background: "#c01e1e",
                                margin: '0px',
                            }}
                            onClick={handleDelete}
                        >
                            {deleteLabel}
                        </button>
                    </div>                    

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
