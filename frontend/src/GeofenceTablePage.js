import { useEffect, useMemo, useState } from "react";

import {
    MaterialReactTable,
    useMaterialReactTable,
} from "material-react-table";

import {
    IconButton,
    Tooltip,
} from "@mui/material";

import DeleteIcon from "@mui/icons-material/Delete";

import {
    get_all_geofences,
    delete_geofence,
} from "./utils";

export default function GeofenceTablePage() {

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    async function loadData() {

        setLoading(true);

        try {
            const result = await get_all_geofences();
            if (result?.error) {
                alert(`Error loading geofences: ${result.error}`);
            } else if (result?.status && result.status >= 400) {
                alert(`Error loading geofences: Status ${result.status}`);
            }
            setData(result?.data ?? []);
        } catch (err) {
            console.error(err);
            alert(`Error loading geofences: ${err}`);
        }

        setLoading(false);

    }

    useEffect(() => {
        loadData();
    }, []);

    async function handleDelete(row) {

        if (
            !window.confirm(
                `Delete "${row.geofence_name}"?`
            )
        ) {
            return;
        }

        try {
            const res = await delete_geofence({
                geofence_id: row.geofence_id,
                geofence_name: row.geofence_name,
            });
            if (res?.error) {
                alert(`Error deleting geofence: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                alert(`Error deleting geofence: Status ${res.status}`);
            } else {
                loadData();
            }
        } catch (err) {
            console.error(err);
            alert(`Error deleting geofence: ${err}`);
        }

    }

    const columns = useMemo(
        () => [
            {
                accessorKey: "geofence_name",
                header: "Name",
            },
            {
                accessorKey: "geofence_description",
                header: "Description",
                enableColumnFilter: false,
            },
            {
                accessorFn: row =>
                    row.geofence_polygon?.length ?? 0,
                id: "vertices",
                header: "Vertices",
                enableColumnFilter: false,
            },
        ],
        []
    );

    const table = useMaterialReactTable({

        columns,
        data,

        enableColumnFilters: true,
        enableGlobalFilter: false,

        state: {
            isLoading: loading,
        },

        renderRowActions: ({ row }) => (

            <Tooltip title="Delete">

                <IconButton
                    color="error"
                    onClick={() => handleDelete(row.original)}
                >
                    <DeleteIcon />
                </IconButton>

            </Tooltip>

        ),

        enableRowActions: true,

        positionActionsColumn: "last",

    });

    return (
        <div style={{ padding: "20px" }}>
            <h1>Geofences</h1>
            <MaterialReactTable table={table} />
        </div>
    );
}
