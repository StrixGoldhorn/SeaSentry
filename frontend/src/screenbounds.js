import React, { useState } from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Child component to handle map events
export function MapBoundsTracker({ onBoundsChange }) {
  const map = useMapEvents({
    // Fires whenever the user finishes dragging or zooming
    moveend() {
      const bounds = map.getBounds();
      
      // Extract structural details
      const lat_min = bounds.getSouth();
      const lat_max = bounds.getNorth();
      const long_min = bounds.getEast();
      const long_max = bounds.getWest();

      onBoundsChange({
        lat_min, lat_max, long_min, long_max
      });
    },
  });

  return null; // This component handles logic, it doesn't render HTML
}