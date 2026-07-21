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

    useEffect(() => {
        const timeout = setTimeout(() => {
            async function load() {
                setLoading(true);

                const startTime = new Date(
                    Date.now() - historyWindow * 60 * 60 * 1000
                ).toISOString();

                const [shipRes, historyRes] = await Promise.all([
                    get_ship_using_data_id({
                        vessel_data_id: Number(vesselDataId),
                    }),

                    get_ship_location_history({
                        vessel_data_id: Number(vesselDataId),
                        start_time_str: startTime,
                    })
                ]);

                setVessel(shipRes?.data ?? null);
                setHistory(historyRes?.data ?? []);

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
            <VesselHistoryMap
                vessel={vessel}
                history={history}
                historyWindow={historyWindow}
            />

            <VesselHistorySidebar
                vessel={vessel}
                history={history}
                historyWindow={historyWindow}
                setHistoryWindow={setHistoryWindow}
                maxHistoryWindow={maxHistoryWindow}
                setMaxHistoryWindow={setMaxHistoryWindow}
            />
        </div>
    );
}