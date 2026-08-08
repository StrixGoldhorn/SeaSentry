import { useEffect, useState } from "react";
import { get_all_VOI, delete_VOI } from "./utils";

export default function VOIList({
    onEdit,
    refreshKey,
}) {

    const [vois, setVOIs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        refresh();
    }, [refreshKey]);

    async function refresh() {
        setLoading(true);

        try {
            const data = await get_all_VOI();
            if (data?.error) {
                alert(`Error loading VOIs: ${data.error}`);
            } else if (data?.status && data.status >= 400) {
                alert(`Error loading VOIs: Status ${data.status}`);
            }
            if (data?.data) {
                setVOIs(data.data);
            }
        } catch (err) {
            console.error(err);
            alert(`Error loading VOIs: ${err}`);
        }

        setLoading(false);
    }

    useEffect(() => {
        refresh();
    }, []);

    async function handleDelete(voi) {

        const confirmed = window.confirm(
            `Delete "${voi.vessel_of_interest_desc_name}"?`
        );

        if (!confirmed) return;

        try {
            const res = await delete_VOI({
                voi_id: voi.vessel_of_interest_id,
                voi_name: voi.vessel_of_interest_desc_name
            });
            if (res?.error) {
                alert(`Error deleting VOI: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                alert(`Error deleting VOI: Status ${res.status}`);
            } else {
                refresh();
            }
        } catch (err) {
            console.error(err);
            alert(`Error deleting VOI: ${err}`);
        }
    }

    if (loading) {
        return <p>Loading...</p>;
    }

    return (

        <div className="alert-rule">

            <h2>Vessels of Interest</h2>

            {vois.length === 0 && (
                <p>No vessels of interest.</p>
            )}

            {vois.map(voi => (

                <div
                    key={voi.vessel_of_interest_id}
                    style={{
                        border: "1px solid gray",
                        padding: "12px",
                        marginBottom: "10px",
                        borderRadius: "8px"
                    }}
                >

                    <h3>{voi.vessel_of_interest_desc_name}</h3>

                    <p>
                        <strong>Description:</strong>{" "}
                        {voi.vessel_of_interest_description || "None"}
                    </p>

                    <p>
                        <strong>MMSI:</strong>{" "}
                        {voi.vessel_of_interest_mmsi ?? "None"}
                    </p>

                    <p>
                        <strong>IMO:</strong>{" "}
                        {voi.vessel_of_interest_imo ?? "None"}
                    </p>

                    <button
                        onClick={() => onEdit?.(voi)}
                    >
                        Edit
                    </button>

                    <button
                        onClick={() => handleDelete(voi)}
                        style={{
                            background: "#cc3333",
                            color: "white",
                            border: "none",
                            padding: "6px 12px",
                            cursor: "pointer"
                        }}
                    >
                        Delete
                    </button>

                </div>

            ))}

        </div>

    );

}