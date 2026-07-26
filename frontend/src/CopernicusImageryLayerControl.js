import React, { useState, useEffect } from 'react';
import { WMSTileLayer } from 'react-leaflet';

const CopernicusImageryLayerControl = ({
    instanceId,
    setInstanceId,
    selectedLayer,
    setSelectedLayer,
}) => {
  const handleResetId = () => {
    localStorage.removeItem('sentinelHubInstanceId');
    setInstanceId('');
    setSelectedLayer('none');
    const newId = window.prompt("Enter new Instance ID:");
    if (newId != "") {
      localStorage.setItem('sentinelHubInstanceId', newId);
      setInstanceId(newId);
    }
  };

  if (!instanceId) {
      return (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <h2>Sentinel Imagery</h2>

              <p>Instance ID not set.</p>

              <button
                  onClick={() => {
                      const newId = window.prompt(
                          "Please enter your Sentinel Hub Instance ID:"
                      );

                      if (newId) {
                          localStorage.setItem(
                              "sentinelHubInstanceId",
                              newId
                          );
                          setInstanceId(newId);
                      }
                  }}
              >
                  Set Instance ID
              </button>
          </div>
      );
  }

  return (
    <div
        style={{
            width: 300,
            padding: 20,
            background: "white"
        }}
    >
      <div>
        <h2>Sentinel Imagery</h2>
        <button 
          onClick={handleResetId}
          style={{ fontSize: '12px', cursor: 'pointer', background: '#f0f0f0', border: '1px solid #ccc', color: '#555', borderRadius: '4px' }}
          title="Change Instance ID"
        >
          Reset ID
        </button>
      </div>
      
      <label style={{ display: 'flex', marginBottom: '5px', fontWeight: 'bold', fontSize: '14px' }}>Select Layer:</label>
      <select 
        value={selectedLayer} 
        onChange={(e) => setSelectedLayer(e.target.value)} 
        style={{ width: '80%', padding: '8px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
      >
        <option value="none">None</option>
        <option value="sentinel2">Sentinel-2 (Optical)</option>
        <option value="sentinel1">Sentinel-1 (SAR)</option>
      </select>

      
      <p style={{ fontSize: '12px', color: '#555', marginTop: '10px', lineHeight: '1.4' }}>
        Ensure the layer names match your Sentinel Hub configuration.
      </p>
    </div>
  );
};

export default CopernicusImageryLayerControl;