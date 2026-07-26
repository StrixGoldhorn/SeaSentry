import { useState } from "react";
import { export_area } from "./utils";

export default function ExportAreaSidebar({
    bounds,
    setBounds
}) {

    const [startTime, setStartTime] = useState("");
    const [endTime, setEndTime] = useState("");
    const [format, setFormat] = useState("geojson");

    const handleExport = async () => {

        if (!bounds) {
            alert("Please draw a rectangle.");
            return;
        }

        const blob = await export_area({
            ...bounds,
            start_time: startTime
                ? new Date(startTime).toISOString()
                : null,
            end_time: endTime
                ? new Date(endTime).toISOString()
                : null,
            format
        });

        if (!blob) return;

        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");

        a.href = url;
        a.download = `vessel_export.${format}`;

        a.click();

        window.URL.revokeObjectURL(url);
    };

    return (
        <div style={{ width: 300 }}>

            <h2>Export Area</h2>

            <p>
                Draw a rectangle on the map.
            </p>

            <input
                type="datetime-local"
                value={startTime}
                onChange={(e)=>setStartTime(e.target.value)}
                style={{ width:"100%" }}
            />

            <input
                type="datetime-local"
                value={endTime}
                onChange={(e)=>setEndTime(e.target.value)}
                style={{
                    width:"100%",
                    marginTop:10
                }}
            />

            <select
                value={format}
                onChange={(e)=>setFormat(e.target.value)}
                style={{
                    width:"100%",
                    marginTop:10
                }}
            >
                <option value="json">JSON</option>
                <option value="geojson">GeoJSON</option>
                <option value="csv">CSV</option>
            </select>

            <button
                onClick={handleExport}
                style={{
                    width:"100%",
                    marginTop:15
                }}
            >
                Export
            </button>

            <button
                onClick={()=>setBounds(null)}
                style={{
                    width:"100%",
                    marginTop:10
                }}
            >
                Clear Rectangle
            </button>

        </div>
    );
}
