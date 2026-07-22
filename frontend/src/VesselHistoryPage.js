import { useEffect, useState } from "react";
import { useParams } from "react-router";

import VesselHistoryMap from "./VesselHistoryMap";
import VesselHistorySidebar from "./VesselHistorySidebar";

import {
    get_ship_location_history,
    get_ship_using_data_id,
} from "./utils";

export default function VesselHistoryPage() {
    const { vesselDataId } = useParams();

    const [loading, setLoading] = useState(true);
    const [vessel, setVessel] = useState(null);
    const [history, setHistory] = useState([]);
    const [historyWindow, setHistoryWindow] = useState(24);
    const [maxHistoryWindow, setMaxHistoryWindow] = useState(168);

    const [historyError, setHistoryError] = useState(null);

    useEffect(() => {
        const timeout = setTimeout(() => {
            async function load() {
                setLoading(true);
                setHistoryError(null);

                const startTime = new Date(
                    Date.now() - historyWindow * 60 * 60 * 1000
                ).toISOString();

                try {
                    const shipRes = await get_ship_using_data_id({
                        vessel_data_id: Number(vesselDataId),
                    });

                    setVessel(shipRes?.data ?? null);

                    const historyRes = await get_ship_location_history({
                        vessel_data_id: Number(vesselDataId),
                        start_time_str: startTime,
                    });

                    if (
                        historyRes?.error === "No history exists."
                    ) {
                        setHistory([]);
                        setHistoryError("No vessel history exists for the selected time range.");
                    } else {
                        setHistory(historyRes?.data ?? []);
                    }
                } catch (err) {
                    console.error(err);
                    setHistory([]);
                    setHistoryError("Failed to load vessel history.");
                }

                setLoading(false);
            }

            load();

        }, 500); 

        return () => clearTimeout(timeout);

    }, [vesselDataId, historyWindow]);

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div
            style={{
                display: "flex",
                width: "100%",
                height: "100vh",
            }}
        >
        {historyError ? (
            <div
                style={{
                    width: "70%",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    fontSize: "1.2rem",
                    color: "#666",
                }}
            >
                {historyError}
            </div>
        ) : (
            <VesselHistoryMap
                vessel={vessel}
                history={history}
                historyWindow={historyWindow}
            />
        )}
            <VesselHistorySidebar
                vessel={vessel}
                history={history}
                historyError={historyError}
                historyWindow={historyWindow}
                setHistoryWindow={setHistoryWindow}
                maxHistoryWindow={maxHistoryWindow}
                setMaxHistoryWindow={setMaxHistoryWindow}
            />
        </div>
    );
}