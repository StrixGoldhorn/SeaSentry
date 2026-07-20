import React, { useState, useEffect } from 'react';
import { WMSTileLayer } from 'react-leaflet';

const CopernicusImageryLayerControl = () => {
  const [instanceId, setInstanceId] = useState('');
  const [selectedLayer, setSelectedLayer] = useState('none');

  useEffect(() => {
    // Load from localStorage on mount
    const savedId = localStorage.getItem('sentinelHubInstanceId');
    if (savedId) {
      setInstanceId(savedId);
    }
  }, []);

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
      <div style={{ position: 'absolute', bottom: 80, left: 20, zIndex: 1000, background: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.3)', width: '250px' }}>
        <h4 style={{ marginTop: 0, marginBottom: '10px' }}>Sentinel Imagery</h4>
        <p style={{ fontSize: '14px', marginBottom: '10px', color: '#555' }}>Instance ID not set.</p>
        <button 
          onClick={() => {
            const newId = window.prompt("Please enter your Sentinel Hub Instance ID:");
            if (newId) {
              localStorage.setItem('sentinelHubInstanceId', newId);
              setInstanceId(newId);
            }
          }}
          style={{ width: '100%', padding: '8px', cursor: 'pointer', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Set Instance ID
        </button>
      </div>
    );
  }

  return (
    <div style={{ position: 'absolute', bottom: 20, left: 20, zIndex: 1000, background: 'white', padding: '10px', borderRadius: '8px', width: '400px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2 style={{ margin: 0 }}>Sentinel Imagery</h2>
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

      {selectedLayer === 'sentinel2' && (
        <WMSTileLayer
          url={`https://sh.dataspace.copernicus.eu/ogc/wms/${instanceId}`}
          layers="TRUE_S2L2A"
          format="image/png"
          transparent={true}
          version="1.3.0"
          attribution='Sentinel-2 imagery'
        />
      )}

      {selectedLayer === 'sentinel1' && (
        <WMSTileLayer
          url={`https://sh.dataspace.copernicus.eu/ogc/wms/${instanceId}`}
          layers="SAR_VV_VH" 
          format="image/png"
          transparent={true}
          version="1.3.0"
          attribution='Sentinel-1 imagery'
        />
      )}
      
      <p style={{ fontSize: '12px', color: '#555', marginTop: '10px', lineHeight: '1.4' }}>
        Ensure the layer names match your Sentinel Hub configuration.
      </p>
    </div>
  );
};

export default CopernicusImageryLayerControl;