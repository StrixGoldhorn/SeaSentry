import { useEffect, useState } from "react";

import { get_all_alert_history, mark_alert_read, mark_alert_unread} from "./utils";

export default function AlertHistoryPage() {

    const [alerts, setAlerts] = useState([]);

    const [filters, setFilters] = useState({
        start_time: "",
        end_time: ""
    });

    const [loading, setLoading] = useState(false);

    const loadAlerts = async () => {

        setLoading(true);

        const data = await get_all_alert_history({

            start_time:
                filters.start_time || null,

            end_time:
                filters.end_time || null,

            limit: 100,

            offset: 0
        });

        if (data?.data) {
            setAlerts(data.data);
        } else if (Array.isArray(data)) {
            setAlerts(data);
        }

        setLoading(false);
    };

    useEffect(() => {
        loadAlerts();
    }, []);

    const toggleReadStatus = async (alert) => {

        const id =
            alert.alert_history_id ??
            alert.id;

        const isRead =
            alert.is_read ??
            alert.read ??
            false;

        if (isRead) {

            await mark_alert_unread({
                alert_history_id: id
            });

        } else {

            await mark_alert_read({
                alert_history_id: id
            });

        }

        await loadAlerts();
    };

    return (

        <div
            style={{
                padding: "20px"
            }}
        >

            <h1>Alert History</h1>

            <div
                style={{
                    display: "flex",
                    gap: "10px",
                    marginBottom: "20px"
                }}
            >

                <div>

                    <div>Start Time</div>

                    <input
                        type="datetime-local"
                        value={filters.start_time}
                        onChange={(e) =>
                            setFilters({
                                ...filters,
                                start_time: e.target.value
                            })
                        }
                    />

                </div>

                <div>

                    <div>End Time</div>

                    <input
                        type="datetime-local"
                        value={filters.end_time}
                        onChange={(e) =>
                            setFilters({
                                ...filters,
                                end_time: e.target.value
                            })
                        }
                    />

                </div>

                <button
                    onClick={loadAlerts}
                >
                    Search
                </button>

            </div>

            {loading && (
                <div>Loading...</div>
            )}

            {!loading && alerts.length === 0 && (
                <div>No alerts found.</div>
            )}

            {alerts.map(alert => {

                const id =
                    alert.alert_history_id ??
                    alert.id;

                const isRead =
                    alert.is_read ??
                    alert.read ??
                    false;

                return (

                    <div
                        key={id}
                        style={{
                            border: "1px solid gray",
                            borderRadius: "8px",
                            padding: "12px",
                            marginBottom: "12px"
                        }}
                    >

                        <h3>
                            Alert #{id}
                        </h3>

                        <p>
                            <strong>Status:</strong>
                            {" "}
                            {isRead
                                ? "Read"
                                : "Unread"}
                        </p>

                        {alert.timestamp && (
                            <p>
                                <strong>Timestamp:</strong>
                                {" "}
                                {alert.timestamp}
                            </p>
                        )}

                        {alert.message && (
                            <p>
                                <strong>Message:</strong>
                                {" "}
                                {alert.message}
                            </p>
                        )}

                        {alert.alert_name && (
                            <p>
                                <strong>Rule:</strong>
                                {" "}
                                {alert.alert_name}
                            </p>
                        )}

                        <button
                            onClick={() =>
                                toggleReadStatus(alert)
                            }
                        >
                            Mark as {isRead ? "Unread" : "Read"}
                        </button>

                        <details
                            style={{
                                marginTop: "10px"
                            }}
                        >
                            <summary>
                                Show Full JSON
                            </summary>

                            <pre>
                                {JSON.stringify(
                                    alert,
                                    null,
                                    2
                                )}
                            </pre>

                        </details>

                    </div>

                );

            })}

        </div>

    );
}