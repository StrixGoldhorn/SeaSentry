export default function HelpPage() {
    const pageStyle = {
        padding: "40px",
        color: "var(--pri-c)",
        minHeight: "100vh",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    };

    const cardStyle = {
        backgroundColor: "var(--pri)",
        color: "var(--pri-c)",
        padding: "25px",
        borderRadius: "12px",
        marginBottom: "25px",
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
        border: "1px solid var(--pri-c)"
    };

    const highlightStyle = {
        color: "var(--sec-c)",
        fontWeight: "bold",
        backgroundColor: "var(--sec)",
        padding: "2px 4px",
        borderRadius: "4px"
    };

    const tocStyle = {
        backgroundColor: "var(--sec)",
        color: "var(--sec-c)",
        padding: "20px",
        borderRadius: "8px",
        marginBottom: "30px",
        border: "1px solid var(--sec-c)"
    };

    const tocListStyle = {
        listStyleType: "circle",
        paddingLeft: "25px"
    };

    const tocLinkStyle = {
        color: "var(--sec-c)",
        textDecoration: "underline",
        fontWeight: "600",
        display: "block",
        padding: "6px 0"
    };

    return (
        <div style={pageStyle}>
            <h1>SeaSentry User Guide</h1>
            <p>Welcome to SeaSentry. Follow the sections below to get started and master the maritime monitoring workflow!</p><br/>

            <div style={tocStyle}>
                <h2>Table of Contents</h2>
                <ul style={tocListStyle}>
                    <li><a href="#workflow" style={tocLinkStyle}>Core Workflow for Beginners</a></li>
                    <li><a href="#map-page" style={tocLinkStyle}>Map Page</a></li>
                    <li><a href="#vessels-page" style={tocLinkStyle}>Vessels Page</a></li>
                    <li><a href="#vois-page" style={tocLinkStyle}>VOIs Page</a></li>
                    <li><a href="#aois-page" style={tocLinkStyle}>AOIs Page</a></li>
                    <li><a href="#geofences-page" style={tocLinkStyle}>Geofences Page</a></li>
                    <li><a href="#add-via-coords-page" style={tocLinkStyle}>Add via coords Page</a></li>
                    <li><a href="#alert-rules-page" style={tocLinkStyle}>Alert Rules Page</a></li>
                    <li><a href="#all-alerts-page" style={tocLinkStyle}>All Alerts Page</a></li>
                    <li><a href="#vessel-history-page" style={tocLinkStyle}>Vessel History Page</a></li>
                    <li><a href="#managing-areas" style={tocLinkStyle}>Managing Areas (AOIs vs Geofences)</a></li>
                    <li><a href="#data-export" style={tocLinkStyle}>Data Export & Reporting</a></li>
                    <li><a href="#satellite-imagery" style={tocLinkStyle}>Satellite Imagery & Copernicus</a></li>
                    <li><a href="#external-integrations" style={tocLinkStyle}>External Integrations (Advanced)</a></li>
                    <li><a href="#troubleshooting" style={tocLinkStyle}>Troubleshooting & FAQ</a></li>
                </ul>
            </div>

            <div id="workflow" style={cardStyle}>
                <h2>Core Workflow for Beginners</h2>
                <p>Follow these steps to set up your maritime monitoring:</p>
                <ol>
                    <li><strong>Define an AOI:</strong> Go to the <span style={highlightStyle}>Map</span>, click the "Add AOI" tool on the left, and draw a region. The system will only scrape and record vessel data within your AOIs.</li>
                    <li><strong>Set a Geofence:</strong> Draw a Geofence inside or around your AOI if you want to trigger alerts for specific zones (e.g., ports, restricted waters).</li>
                    <li><strong>Create Alert Rules:</strong> Navigate to <span style={highlightStyle}>Alert Rules</span> and set up conditions like "Inside Geofence" + "Speed > 10 knots".</li>
                    <li><strong>Monitor:</strong> Watch the Map in real-time or check <span style={highlightStyle}>All Alerts</span> for rule violations.</li>
                </ol>
            </div>

            <div id="map-page" style={cardStyle}>
                <h2>Map Page</h2>
                <p>The Map is your primary dashboard. It displays vessels, AOIs, and Geofences.</p>
                <ul>
                    <li><strong>Sidebar Tools:</strong> Use the left sidebar to draw AOIs/Geofences, toggle Satellite Imagery (Sentinel), export area data, and filter by ship type.</li>
                    <li><strong>Vessel Heatmap:</strong> Toggle the "Vessel Heatmap" in the top-right layers control to see historical density.</li>
                    <li><strong>Vessel Popups:</strong> Click any ship to see its MMSI, speed, heading, and a button to view its detailed location history.</li>
                    <li><strong>Imagery:</strong> Enter your Sentinel Hub Instance ID to overlay real-time optical or SAR satellite imagery.</li>
                </ul>
            </div>

            <div id="vessels-page" style={cardStyle}>
                <h2>Vessels Page</h2>
                <p>A tabular view of all ships the system has ever recorded.</p>
                <ul>
                    <li>You can search by Name, MMSI, IMO, or Type using the column filters.</li>
                    <li>Use the "View" action to see the vessel's latest location on the map, or the "Edit" action to manually update vessel details like Name or Type.</li>
                </ul>
            </div>

            <div id="vois-page" style={cardStyle}>
                <h2>VOIs Page</h2>
                <p>Manage your Vessels of Interest.</p>
                <ul>
                    <li>Add specific ships (by MMSI or IMO) that you want to closely monitor.</li>
                    <li>You can use the "Is Vessel Of Interest" condition in Alert Rules.</li>
                </ul>
            </div>

            <div id="aois-page" style={cardStyle}>
                <h2>AOIs Page</h2>
                <p>A tabular view of all your Areas of Interest.</p>
                <ul>
                    <li>Review the name, description, and vertex count of all drawn AOIs.</li>
                    <li>Delete AOIs that are no longer needed. <strong>Note:</strong> Deleting an AOI will stop data collection for that specific region.</li>
                </ul>
            </div>

            <div id="geofences-page" style={cardStyle}>
                <h2>Geofences Page</h2>
                <p>A tabular view of all your Geofences.</p>
                <ul>
                    <li>Review existing Geofences used for alert boundaries.</li>
                    <li>Delete any outdated Geofences.</li>
                </ul>
            </div>

            <div id="add-via-coords-page" style={cardStyle}>
                <h2>Add via coords Page</h2>
                <p>Manually create precise AOIs and Geofences using exact coordinates.</p>
                <ul>
                    <li>Enter a name, description, and minimum/maximum Latitude and Longitude to generate a bounding box area.</li>
                    <li>Useful when you have exact coordinate boundaries instead of visually drawing them on the map.</li>
                </ul>
            </div>

            <div id="alert-rules-page" style={cardStyle}>
                <h2>Alert Rules Page</h2>
                <p>Automate your monitoring using a flexible rule builder.</p>
                <ul>
                    <li>Create rules using AND/OR logic.</li>
                    <li>Triggers can include Speed, Ship Type, Proximity to other ships, or Geofence entry/exit.</li>
                    <li>Enable or disable rules dynamically.</li>
                </ul>
            </div>

            <div id="all-alerts-page" style={cardStyle}>
                <h2>All Alerts Page</h2>
                <p>View a history of every time a rule was triggered.</p>
                <ul>
                    <li>See the timestamp, the matched vessels, and the specific rule that generated the alert.</li>
                    <li>Mark them as Read/Unread to manage your inbox and filter the view.</li>
                </ul>
            </div>

            <div id="vessel-history-page" style={cardStyle}>
                <h2>Vessel History Page</h2>
                <p>A dedicated view for analyzing a single vessel's past movements.</p>
                <ul>
                    <li>Adjust the time window slider to see tracks over the last X hours (up to a configurable maximum).</li>
                    <li>Review all pinged locations with a connected track, and inspect details like speed and heading at every recorded point.</li>
                </ul>
            </div>
            
            <div id="managing-areas" style={cardStyle}>
                <h2>Managing Areas (AOIs vs Geofences)</h2>
                <p>Understanding the difference between the two area types is crucial:</p>
                <ul>
                    <li><span style={highlightStyle}>AOIs (Areas of Interest):</span> Define where the system actively scrapes and records data. You must have an AOI for vessels to appear!</li>
                    <li><span style={highlightStyle}>Geofences:</span> Logical boundaries used purely for Alert Rules (e.g., "Alert when ship enters Geofence A").</li>
                </ul>
                <p>You can add these visually on the Map, or precisely using coordinates via the <span style={highlightStyle}>Add via coords</span> page.</p>
            </div>

            <div id="data-export" style={cardStyle}>
                <h2>Data Export & Reporting</h2>
                <p>You can export historical vessel data directly from the Map.</p>
                <ul>
                    <li><span style={highlightStyle}>Export Area Tool:</span> Open the Export tool from the left sidebar and draw a rectangle over the region you want to extract data from.</li>
                    <li><span style={highlightStyle}>Formats:</span> Select JSON, GeoJSON, or CSV as your export format.</li>
                    <li><span style={highlightStyle}>Time Range:</span> Optionally pick a Start and End Time to filter exactly which data points are included in the export file.</li>
                </ul>
            </div>

            <div id="satellite-imagery" style={cardStyle}>
                <h2>Satellite Imagery & Copernicus</h2>
                <p>Enhance your situational awareness by overlaying live satellite imagery from Sentinel Hub.</p>
                <ul>
                    <li><span style={highlightStyle}>Sentinel-2 (Optical):</span> Provides true-color optical imagery. Best used for clear, daytime conditions to visually spot vessels.</li>
                    <li><span style={highlightStyle}>Sentinel-1 (SAR):</span> Synthetic Aperture Radar imagery. Pierces through clouds and works at night, making it excellent for all-weather ship detection.</li>
                    <li><strong>Setup:</strong> You must configure a Sentinel Hub Instance ID via the "Satellite Imagery" tool on the Map page.</li>
                </ul>
            </div>

            <div id="external-integrations" style={cardStyle}>
                <h2>External Integrations (Advanced)</h2>
                <p>SeaSentry supports external data sources:</p>
                <ul>
                    <li><strong>ATAK:</strong> Connect your device to the FreeTakServer. Broadcast an AOI polygon from ATAK to receive vessel tracks directly on your device.</li>
                    <li><strong>SDR / NMEA 0183:</strong> You can stream local AIS data (via AIS-Catcher) into the backend UDP socket to supplement scraped data.</li>
                </ul>
            </div>

            <div id="troubleshooting" style={cardStyle}>
                <h2>Troubleshooting & FAQ</h2>
                <ul>
                    <li><strong>Why are there no ships on my map?</strong><br/>Make sure you have drawn an AOI. The system only tracks data inside these areas. Wait a few moments after drawing an AOI, or click on the AOI and force scrape, for the scraper to pick up new tracks.</li>
                    <li><strong>Why aren't my alerts triggering?</strong><br/>Check the <span style={highlightStyle}>Alert Rules</span> page to ensure your rule is marked as "Enabled". Also verify that the conditions don't contradict each other (e.g. using AND when you meant OR). Furthermore, wait for a few minutes. The time taken for each alert rescan is dependent on your config file.</li>
                    <li><strong>Why isn't the satellite layer showing?</strong><br/>Ensure your Sentinel Hub Instance ID is correct and that you've selected a specific layer (Sentinel-1 or Sentinel-2) from the sidebar.</li>
                    <li><strong>Can I manually force a scrape?</strong><br/>Yes. Click on an existing AOI polygon on the Map and click the "Scrape AOI" button in the popup popup. Note: Do not spam this button to avoid getting rate-limited and/or IP-blocked by the website it scrapes from.</li>
                </ul>
            </div>
        </div>
    );
}