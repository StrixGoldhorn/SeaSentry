import { useEffect, useMemo, useState } from "react";
import {
  MaterialReactTable,
  useMaterialReactTable,
} from "material-react-table";

import {
  Button,
  IconButton,
  Tooltip,
} from "@mui/material";

import EditIcon from "@mui/icons-material/Edit";
import VisibilityIcon from "@mui/icons-material/Visibility";
import { useNavigate } from "react-router";


import { get_all_ships } from "./utils";
import VesselEditDialog from "./VesselEditDialog";

export default function VesselTablePage() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);
  const [rowCount, setRowCount] = useState(0);

  const [loading, setLoading] = useState(false);

  const [globalFilter, setGlobalFilter] = useState("");
  const [columnFilters, setColumnFilters] = useState([]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 25,
  });

  const [editingShip, setEditingShip] = useState(null);

  useEffect(() => {
    const timer = setTimeout(loadData, 500);
    return () => clearTimeout(timer);
  }, [globalFilter, columnFilters, pagination]);

  useEffect(() => {
        setPagination(p => ({
            ...p,
            pageIndex: 0,
        }));
    }, [columnFilters]);

  async function loadData() {
    setLoading(true);

    const filters = buildSearchParams(columnFilters);

    const result = await get_all_ships({
        ...filters,
        querystr: globalFilter,
        limit: pagination.pageSize,
        offset: pagination.pageIndex * pagination.pageSize,
    });

    setData(result?.data ?? []);
    setRowCount(result.total)

    setLoading(false);
  }

  const columns = useMemo(
    () => [
      {
        accessorKey: "ship_name",
        header: "Name",
        enableSorting: false,
      },
      {
        accessorKey: "mmsi",
        header: "MMSI",
        enableSorting: false,
      },
      {
        accessorKey: "imo",
        header: "IMO",
        enableSorting: false,
      },
      {
        accessorKey: "ship_type",
        header: "Type",
        enableSorting: false,
      },
      {
        accessorKey: "flag",
        header: "Flag",
        enableSorting: false,
      },
      {
        accessorKey: "length_meters",
        header: "Length",
        enableColumnFilter: false,
        enableSorting: false,
      },
      {
        accessorKey: "beam_meters",
        header: "Beam",
        enableColumnFilter: false,
        enableSorting: false,
      },
      {
        accessorFn: row => row.user_tags?.join(", ") ?? "",
        id: "user_tags",
        header: "Tags",
        enableColumnFilter: false,
        enableSorting: false,
      },
    ],
    []
  );

  const table = useMaterialReactTable({
    columns,
    data,

    manualPagination: true,
    manualFiltering: true,

    rowCount,

    enableColumnFilters: true,
    enableGlobalFilter: true,

    state: {
      isLoading: loading,
      globalFilter,
      columnFilters,
      pagination,
    },

    onGlobalFilterChange: setGlobalFilter,
    onColumnFiltersChange: setColumnFilters,

    onPaginationChange: setPagination,

renderRowActions: ({ row }) => (
    <>
        <Tooltip title="View">

            <IconButton
                onClick={() =>
                    navigate(
                        `/vessel/${row.original.vessel_data_id}`
                    )
                }
            >
                <VisibilityIcon/>
            </IconButton>

        </Tooltip>


        <Tooltip title="Edit">

            <IconButton
                onClick={() =>
                    setEditingShip(row.original)
                }
            >
                <EditIcon/>
            </IconButton>

        </Tooltip>
    </>
),

    enableRowActions: true,

    positionActionsColumn: "last",
  });

  return (
    <>

      <MaterialReactTable table={table} />

      {editingShip && (

        <VesselEditDialog

          ship={editingShip}

          onClose={() => setEditingShip(null)}

          onSaved={() => {
            setEditingShip(null);
            loadData();
          }}

        />

      )}

    </>
  );
}


function buildSearchParams(filters) {
    const params = {};

    filters.forEach(filter => {
        switch (filter.id) {
            case "ship_name":
                params.name = filter.value;
                break;

            case "mmsi":
                params.mmsi = filter.value;
                break;

            case "imo":
                params.imo = filter.value;
                break;

            case "ship_type":
                params.shiptype = filter.value;
                break;

            case "flag":
                params.flag = filter.value;
                break;

            default:
                break;
        }
    });

    return params;
}