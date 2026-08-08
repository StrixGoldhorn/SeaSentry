import './styles.css';

import { useEffect, useMemo, useState } from "react";

import {
    get_all_alert_history,
    mark_alert_read,
    mark_alert_unread
} from "./utils";

import {
    MaterialReactTable,
    useMaterialReactTable,
} from "material-react-table";

import { Button } from "@mui/material";


export default function AllAlertHistoryPage() {

    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(false);

    const [ruleFilter, setRuleFilter] = useState("");


    const loadAlerts = async () => {

        setLoading(true);

        try {
            const data = await get_all_alert_history({
                limit: 1000000,
                offset: 0
            });
            if (data?.error) {
                window.alert(`Error loading alert history: ${data.error}`);
            } else if (data?.status && data.status >= 400) {
                window.alert(`Error loading alert history: Status ${data.status}`);
            }
            if (data?.data) {
                setAlerts(data.data);
            } else if (Array.isArray(data)) {
                setAlerts(data);
            }
        } catch (err) {
            console.error(err);
            window.alert(`Error loading alert history: ${err}`);
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
                window.alert(`Error updating alert status: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                window.alert(`Error updating alert status: Status ${res.status}`);
            } else {
                await loadAlerts();
            }
        } catch (err) {
            console.error(err);
            window.alert(`Error updating alert status: ${err}`);
        }
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

        if (!ruleFilter) {
            return alerts;
        }

        return alerts.filter(alert =>
            alert.alert_history_context?.rule_name === ruleFilter
        );

    }, [
        alerts,
        ruleFilter
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
                    marginBottom: "15px"
                }}
            >

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
                        marginLeft: "10px"
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


            <MaterialReactTable
                table={table}
                data={alerts}
                enablePagination
                enableColumnFilters
            />

        </div>

    );
}