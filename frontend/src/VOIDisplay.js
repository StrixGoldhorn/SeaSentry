import { useEffect, useState } from "react";
import { get_all_VOI, delete_VOI } from "./utils";

export default function VOIList() {

    const [vois, setVOIs] = useState([]);
    const [loading, setLoading] = useState(true);

    async function refresh() {
        setLoading(true);

        const data = await get_all_VOI();

        if (data?.data) {
            setVOIs(data.data);
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

        await delete_VOI({
            voi_id: voi.vessel_of_interest_id,
            voi_name: voi.vessel_of_interest_desc_name
        });

        refresh();
    }

    if (loading) {
        return <p>Loading...</p>;
    }

    return (

        <div>

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