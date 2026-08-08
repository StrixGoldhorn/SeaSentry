import './styles.css';

import { useEffect, useMemo, useState } from "react";

import {
    get_all_alert_history,
    mark_alert_read,
    mark_alert_unread,
    force_scan_alerts
} from "./utils";

import {
    MaterialReactTable,
    useMaterialReactTable,
} from "material-react-table";

import { Button, Switch, FormControlLabel } from "@mui/material";
import { useSnackbar } from "./SnackbarContext";


export default function AllAlertHistoryPage() {

    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(false);

    const [ruleFilter, setRuleFilter] = useState("");
    const [showUnreadOnly, setShowUnreadOnly] = useState(false);
    const { showSnackbar } = useSnackbar();


    const loadAlerts = async () => {

        setLoading(true);

        try {
            const data = await get_all_alert_history({
                limit: 1000000,
                offset: 0
            });
            if (data?.error) {
                showSnackbar(`Error loading alert history: ${data.error}`);
            } else if (data?.status && data.status >= 400) {
                showSnackbar(`Error loading alert history: Status ${data.status}`);
            }
            if (data?.data) {
                setAlerts(data.data);
            } else if (Array.isArray(data)) {
                setAlerts(data);
            }
        } catch (err) {
            console.error(err);
            showSnackbar(`Error loading alert history: ${err}`);
        }

        setLoading(false);
    };

    useEffect(() => {
        loadAlerts();
    }, []);



    const toggleReadStatus = async (alert) => {
        try {
            let res;
            if (alert.alert_history_read) {
                res = await mark_alert_unread({
                    alert_history_id:
                        alert.alert_history_id
                });
            } else {
                res = await mark_alert_read({
                    alert_history_id:
                        alert.alert_history_id
                });
            }
            if (res?.error) {
                showSnackbar(`Error updating alert status: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                showSnackbar(`Error updating alert status: Status ${res.status}`);
            } else {
                showSnackbar(`Alert marked as ${alert.alert_history_read ? "unread" : "read"}`, "success");
                await loadAlerts();
            }
        } catch (err) {
            console.error(err);
            showSnackbar(`Error updating alert status: ${err}`);
        }
    };

    const markAllAsRead = async () => {
        const unreadAlerts = filteredAlerts.filter(a => !a.alert_history_read);
        if (unreadAlerts.length === 0) return;
        
        if (!window.confirm(`Are you sure you want to mark all ${unreadAlerts.length} alerts as read?`)) {
            return;
        }
        
        setLoading(true);
        try {
            await Promise.all(unreadAlerts.map(alert => 
                mark_alert_read({ alert_history_id: alert.alert_history_id })
            ));
            showSnackbar("All alerts marked as read", "success");
        } catch (err) {
            console.error(err);
            showSnackbar(`Error marking all as read: ${err}`);
        }
        await loadAlerts();
    };

    const forceScan = async () => {
        setLoading(true);
        try {
            const res = await force_scan_alerts();
            if (res?.error) {
                showSnackbar(`Error forcing scan: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                showSnackbar(`Error forcing scan: Status ${res.status}`);
            } else {
                showSnackbar("Alert scan triggered successfully", "success");
                await loadAlerts();
            }
        } catch (err) {
            console.error(err);
            showSnackbar(`Error forcing scan: ${err}`);
        }
        setLoading(false);
    };

    const ruleOptions = useMemo(() => {

        const rules = alerts.map(
            alert =>
                alert.alert_history_context?.rule_name
        )
        .filter(Boolean);

        return [
            ...new Set(rules)
        ];

    }, [alerts]);



    const filteredAlerts = useMemo(() => {

        let result = alerts;

        if (showUnreadOnly) {
            result = result.filter(alert => !alert.alert_history_read);
        }

        if (ruleFilter) {
            result = result.filter(alert =>
                alert.alert_history_context?.rule_name === ruleFilter
            );
        }

        return result;

    }, [
        alerts,
        ruleFilter,
        showUnreadOnly
    ]);



const columns = [
    {
        accessorKey: "alert_history_id",
        header: "ID",
    },

    {
        accessorKey: "alert_history_timestamp",
        header: "Timestamp",
        Cell: ({ cell }) =>
            new Date(cell.getValue()).toLocaleString(),
    },

    {
        accessorKey: "alert_history_context.rule_name",
        id: "rule_name",
        header: "Alert Rule",
    },

    {
        accessorKey: "alert_history_read",
        header: "Status",
        filterVariant: "select",
        filterSelectOptions: [
            {
                label: "Read",
                value: true,
            },
            {
                label: "Unread",
                value: false,
            },
        ],
        filterFn: (row, id, filterValue) => {
            return row.getValue(id) === filterValue;
        },
        Cell: ({ cell }) =>
            cell.getValue()
                ? "Read"
                : "Unread",
    },

    {
        accessorKey: "alert_history_context.matched_vessels",
        id: "matched_vessels",
        header: "Matched Vessels",

        filterFn: (row, columnId, filterValue) => {
            const vessels = row.original.alert_history_context?.matched_vessels || [];

            const search = filterValue
                .toLowerCase()
                .trim();

            if (!search) {
                return true;
            }

            return vessels.some(vessel =>
                [
                    vessel.ship_name,
                    vessel.mmsi,
                    vessel.ship_type,
                ]
                .filter(Boolean)
                .some(value =>
                    String(value)
                        .toLowerCase()
                        .includes(search)
                )
            );
        },

        Cell: ({ cell }) => {
            const vessels = cell.getValue() || [];

            return (
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {vessels.map(vessel => (
                        <li key={vessel.ship_data_id}>
                            {vessel.ship_name} ({vessel.mmsi})
                            {vessel.ship_type && 
                                ` - ${vessel.ship_type}`
                            }
                        </li>
                    ))}
                </ul>
            );
        },
    },

    {
        id: "actions",
        header: "Actions",
        enableColumnFilter: false,
        Cell: ({ row }) => {
            const alert = row.original;

            return (
                <Button
                    variant="contained"
                    size="small"
                    color={
                        alert.alert_history_read
                            ? "warning"
                            : "primary"
                    }
                    onClick={() =>
                        toggleReadStatus(alert)
                    }
                >
                    Mark as{" "}
                    {alert.alert_history_read
                        ? "Unread"
                        : "Read"}
                </Button>
            );
        },
    },
];



    const table = useMaterialReactTable({

        columns,

        data: filteredAlerts,

        state: {
            isLoading: loading,
        },


        enablePagination: true,

        initialState: {
            pagination: {
                pageSize: 20,
                pageIndex: 0,
            }
        },


        muiTableContainerProps: {
            sx: {
                maxHeight: "70vh"
            }
        }

    });



    return (

        <div
            style={{
                padding: "20px"
            }}
        >

            <h1>
                Alert History
            </h1>


            <div
                style={{
                    marginBottom: "15px",
                    display: "flex",
                    alignItems: "center",
                    gap: "15px",
                    flexWrap: "wrap"
                }}
            >

                <div>
                <label>
                    Filter by Rule:
                </label>


                <select
                    value={ruleFilter}
                    onChange={(e) =>
                        setRuleFilter(
                            e.target.value
                        )
                    }
                    style={{
                        marginLeft: "10px",
                        padding: "5px"
                    }}
                >

                    <option value="">
                        All Rules
                    </option>

                    {
                        ruleOptions.map(rule => (
                            <option
                                key={rule}
                                value={rule}
                            >
                                {rule}
                            </option>
                        ))
                    }

                </select>
                </div>

                <FormControlLabel
                    control={
                        <Switch
                            checked={showUnreadOnly}
                            onChange={(e) => setShowUnreadOnly(e.target.checked)}
                            color="primary"
                        />
                    }
                    label="Show Unread Only"
                    style={{ margin: 0 }}
                />

                <Button
                    variant="contained"
                    color="primary"
                    onClick={markAllAsRead}
                    disabled={filteredAlerts.filter(a => !a.alert_history_read).length === 0}
                >
                    Mark All Visible As Read
                </Button>

                <Button
                    variant="outlined"
                    color="secondary"
                    onClick={forceScan}
                    disabled={loading}
                >
                    Force Scan
                </Button>
            </div>


            <MaterialReactTable
                table={table}
                data={alerts}
                enablePagination
                enableColumnFilters
            />

        </div>

    );
}