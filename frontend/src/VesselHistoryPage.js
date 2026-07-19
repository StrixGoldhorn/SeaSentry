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
    const [startTime, setStartTime] = useState("");
    const [endTime, setEndTime] = useState("");

    useEffect(() => {
        async function load() {
            setLoading(true);

            const [shipRes, historyRes] = await Promise.all([
                get_ship_using_data_id({
                    vessel_data_id: Number(vesselDataId),
                }),
                get_ship_location_history({
                    vessel_data_id: Number(vesselDataId),
                    start_time_str: startTime
                        ? new Date(startTime).toISOString()
                        : null,
                    end_time_str: endTime
                        ? new Date(endTime).toISOString()
                        : null,
                }),
            ]);

            setVessel(shipRes?.data ?? null);
            setHistory(historyRes?.data ?? []);

            setLoading(false);
        }

        load();
    }, [vesselDataId, startTime, endTime]);

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
                startTime={startTime}
                endTime={endTime}
            />

            <VesselHistorySidebar
                vessel={vessel}
                history={history}
                startTime={startTime}
                endTime={endTime}
                setStartTime={setStartTime}
                setEndTime={setEndTime}
            />
        </div>
    );
}