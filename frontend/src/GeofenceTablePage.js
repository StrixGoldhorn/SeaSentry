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

        const result = await get_all_geofences();

        setData(result?.data ?? []);

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

        await delete_geofence({
            geofence_id: row.geofence_id,
            geofence_name: row.geofence_name,
        });

        loadData();

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
        <MaterialReactTable table={table} />
    );
}
