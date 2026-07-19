import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";
import "leaflet-polylinedecorator";
import { createShipIcon } from "./shipmarkers";
import L from "leaflet";
import { Routes, Route } from "react-router";
import "leaflet/dist/leaflet.css";

import { get_ship_location_history } from "./utils";

function FitBounds({ positions }) {
  const map = useMap();

  useEffect(() => {
    if (positions.length === 0) return;

    map.fitBounds(positions, {
      padding: [40, 40],
    });
  }, [map, positions]);

  return null;
}

function PolylineArrows({ positions }) {
  const map = useMap();

  useEffect(() => {
    if (positions.length < 2) return;

    const polyline = L.polyline(positions);

    const decorator = L.polylineDecorator(polyline, {
      patterns: [
        {
          offset: 25,
          repeat: 50,
          symbol: L.Symbol.arrowHead({
            pixelSize: 10,
            polygon: true,
            pathOptions: {
              color: "#1976d2",
              fillOpacity: 1,
              weight: 2,
            },
          }),
        },
      ],
    });

    decorator.addTo(map);

    return () => {
      map.removeLayer(decorator);
    };
  }, [map, positions]);

  return null;
}

export default function VesselHistoryMap({
    vessel,
    history = [],
    start_time_str = null,
    end_time_str = null,
}) {
    const first = history[0];
    const last = history[history.length - 1];

    const startIcon = createShipIcon(
        vessel?.ship_name,
        first.heading_deg != null,
        vessel?.ship_type,
        18
    );

    const endIcon = createShipIcon(
        vessel?.ship_name,
        last.heading_deg != null,
        vessel?.ship_type,
        28
    );
    
    const [selectedPoint, setSelectedPoint] = useState(null);

    const positions = useMemo(
    () =>
        history.map((p) => [
        p.latitude,
        p.longitude,
        ]),
    [history]
    );

    if (history.length === 0) {
    return <div>No location history found.</div>;
    }

    return (
    <MapContainer
        style={{
        height: "100%",
        width: "70%",
        }}
        center={[
        first.latitude,
        first.longitude,
        ]}
        zoom={13}
        scrollWheelZoom
    >
        <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitBounds positions={positions} />

        <Polyline
        positions={positions}
        pathOptions={{
            color: "#1976d2",
            weight: 4,
        }}
        />

        <PolylineArrows positions={positions} />

        {history.map((point) => (
            <CircleMarker
            key={point.location_id}
            center={[point.latitude, point.longitude]}
            radius={selectedPoint === point.location_id ? 7 : 4}
            pathOptions={{
                color:
                selectedPoint === point.location_id
                    ? "#ff9800"
                    : "#1976d2",
                fillColor:
                selectedPoint === point.location_id
                    ? "#ff9800"
                    : "#1976d2",
                fillOpacity: 0.9,
            }}
            eventHandlers={{
                popupopen: () => setSelectedPoint(point.location_id),
                popupclose: () => setSelectedPoint(null),
            }}
            >
            <Popup>
            <table>
                <tbody>
                <tr>
                    <td><strong>Time</strong></td>
                    <td>{new Date(point.timestamp).toLocaleString()}</td>
                </tr>

                <tr>
                    <td><strong>Latitude</strong></td>
                    <td>{point.latitude.toFixed(6)}</td>
                </tr>

                <tr>
                    <td><strong>Longitude</strong></td>
                    <td>{point.longitude.toFixed(6)}</td>
                </tr>

                <tr>
                    <td><strong>Speed</strong></td>
                    <td>{point.speed_knots ?? "-"} kn</td>
                </tr>

                <tr>
                    <td><strong>Course</strong></td>
                    <td>{point.course_deg ?? "-"}°</td>
                </tr>

                <tr>
                    <td><strong>Heading</strong></td>
                    <td>{point.heading_deg ?? "-"}°</td>
                </tr>

                <tr>
                    <td><strong>Navigation Status</strong></td>
                    <td>{point.nav_status ?? "-"}</td>
                </tr>

                <tr>
                    <td><strong>Rate of Turn</strong></td>
                    <td>{point.rate_of_turn ?? "-"}</td>
                </tr>
                </tbody>
            </table>
            </Popup>
        </CircleMarker>
        ))}

        <Marker
            position={[first.latitude, first.longitude]}
            icon={startIcon}
            rotationOrigin="center"
            rotationAngle={first.heading_deg ?? 0}
        >
            <Popup>
                <b>Start</b>
                <br />
                {new Date(first.timestamp).toLocaleString()}
                <br />
                Speed: {first.speed_knots ?? "-"} kn
            </Popup>
        </Marker>

        <Marker
            position={[last.latitude, last.longitude]}
            icon={endIcon}
            rotationOrigin="center"
            rotationAngle={last.heading_deg ?? 0}
        >
            <Popup>
                <b>End</b>
                <br />
                {new Date(last.timestamp).toLocaleString()}
                <br />
                Speed: {last.speed_knots ?? "-"} kn
            </Popup>
        </Marker>
    </MapContainer>
    );
}