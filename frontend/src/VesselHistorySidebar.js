import "./styles.css";

const getNavStatusString = (navStatus) => {
    const statusMap = {
        0: "Under way using engine",
        1: "At anchor",
        2: "Not under command",
        3: "Restricted manoeuverability",
        4: "Constrained by draught",
        5: "Moored",
        6: "Aground",
        7: "Engaged in fishing",
        8: "Under way sailing",
        9: "Reserved",
        10: "Reserved",
        11: "Reserved",
        12: "Reserved",
        13: "Reserved",
        14: "AIS-SART",
        15: "" // technically shouldn't even happen
    };

  return statusMap[navStatus] ?? "Unknown";
};

export default function VesselHistorySidebar({
    vessel,
    history,
    historyWindow,
    setHistoryWindow,
    maxHistoryWindow,
    setMaxHistoryWindow,
}) {
  if (!vessel) {
    return (
      <div className="history-sidebar">
        Loading vessel...
      </div>
    );
  }

  const first = history?.[history.length - 1];
  const latest = history?.[0];

  return (
    <div className="history-sidebar">

        <div
            style={{
                padding: "12px",
                borderBottom: "1px solid #ccc",
            }}
        >
            <h3>History Filter</h3>

        <label>
            Show last {historyWindow} hours
        </label>

        <input
            type="range"
            min="1"
            max={maxHistoryWindow}
            value={historyWindow}
            onChange={(e) =>
                setHistoryWindow(Number(e.target.value))
            }
            style={{
                width: "100%",
            }}
        />

        <div
            style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginTop: "10px",
            }}
        >
            <label>
                Maximum:
            </label>

            <input
                type="number"
                min="1"
                value={maxHistoryWindow}
                onChange={(e) => {
                    const value = Number(e.target.value);

                    setMaxHistoryWindow(value);

                    if (historyWindow > value) {
                        setHistoryWindow(value);
                    }
                }}
                style={{
                    width: "80px",
                }}
            />

            hours
        </div>
        </div>

      <h2>{vessel.ship_name}</h2>

      <hr />

      <h3>Vessel</h3>

      <table>
        <tbody>
          <tr>
            <td>MMSI</td>
            <td>{vessel.mmsi}</td>
          </tr>

          <tr>
            <td>IMO</td>
            <td>{vessel.imo ?? "-"}</td>
          </tr>

          <tr>
            <td>Type</td>
            <td>{vessel.ship_type ?? "-"}</td>
          </tr>

          <tr>
            <td>Flag</td>
            <td>{vessel.flag ?? "-"}</td>
          </tr>

          <tr>
            <td>Length</td>
            <td>{vessel.length_meters ?? "-"} m</td>
          </tr>

          <tr>
            <td>Beam</td>
            <td>{vessel.beam_meters ?? "-"} m</td>
          </tr>

          <tr>
            <td>Navigation</td>
            <td>{getNavStatusString(vessel.nav_status)}</td>
          </tr>

          <tr>
            <td>Tags</td>
            <td>{vessel.user_tags?.join(", ") || "-"}</td>
          </tr>
        </tbody>
      </table>

      <hr />

      <h3>History</h3>

      <table>
        <tbody>
          <tr>
            <td>Points</td>
            <td>{history.length}</td>
          </tr>

          <tr>
            <td>First Position</td>
            <td>
              {first
                ? new Date(first.timestamp).toLocaleString()
                : "-"}
            </td>
          </tr>

          <tr>
            <td>Latest Position</td>
            <td>
              {latest
                ? new Date(latest.timestamp).toLocaleString()
                : "-"}
            </td>
          </tr>

          <tr>
            <td>Latest Speed</td>
            <td>{latest?.speed_knots ?? "-"} kn</td>
          </tr>

          <tr>
            <td>Latest Course</td>
            <td>{latest?.course_deg ?? "-"}°</td>
          </tr>

          <tr>
            <td>Latest Heading</td>
            <td>{latest?.heading_deg ?? "-"}°</td>
          </tr>
        </tbody>
      </table>

    </div>
  );
}