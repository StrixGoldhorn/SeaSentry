import './styles.css';
import { useEffect, useState } from "react";

import { get_all_alert_history, get_unread_alert_history, mark_alert_read, mark_alert_unread} from "./utils";

export default function AllAlertHistoryPage() {

    const [alerts, setAlerts] = useState([]);

    const [filters, setFilters] = useState({
        start_time: "",
        end_time: ""
    });

    const [loading, setLoading] = useState(false);

    const loadAlerts = async () => {

        setLoading(true);

        const data = await get_unread_alert_history({

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

        const id = alert.alert_history_id;

        const isRead = alert.alert_history_read;

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

                    <p>Start Time</p>

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

                    <p>End Time</p>

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

                const id = alert.alert_history_id;

                const isRead = alert.alert_history_read;

                return (

                    <div
                        key={id}
                        
                        className={
                            isRead
                            ? "alert-card read"
                            : "alert-card"
                        }
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

                        <p>
                            <strong>Timestamp:</strong>{" "}
                            {new Date(alert.alert_history_timestamp).toLocaleString()}
                        </p>

                        <p>
                            <strong>Rule:</strong>{" "}
                            {alert.alert_history_context?.rule_name}
                        </p>

                        {alert.alert_history_context?.matched_vessels?.length > 0 && (
                            <>
                                <p><strong>Matched Vessel:</strong></p>

                                <ul>
                                    {alert.alert_history_context.matched_vessels.map(vessel => (
                                        <li key={vessel.ship_data_id}>
                                            {vessel.ship_name} ({vessel.mmsi})
                                        </li>
                                    ))}
                                </ul>
                            </>
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