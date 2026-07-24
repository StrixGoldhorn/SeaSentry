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
    get_all_AOI,
    delete_AOI,
} from "./utils";

export default function AOITablePage() {

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    async function loadData() {

        setLoading(true);

        const result = await get_all_AOI();

        setData(result?.data ?? []);

        setLoading(false);

    }

    useEffect(() => {
        loadData();
    }, []);

    async function handleDelete(row) {

        if (
            !window.confirm(
                `Delete "${row.area_of_interest_name}"?`
            )
        ) {
            return;
        }

        await delete_AOI({
            aoi_id: row.area_of_interest_id,
            aoi_name: row.area_of_interest_name,
        });

        loadData();

    }

    const columns = useMemo(
        () => [
            {
                accessorKey: "area_of_interest_name",
                header: "Name",
            },
            {
                accessorKey: "area_of_interest_description",
                header: "Description",
                enableColumnFilter: false,
            },
            {
                accessorFn: row =>
                    row.area_of_interest_polygon?.length ?? 0,
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
