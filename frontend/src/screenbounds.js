import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Child component to handle map events
export function MapBoundsTracker({ onBoundsChange }) {
    const map = useMapEvents({
        moveend: updateBounds,
    });

    function updateBounds() {
        const bounds = map.getBounds();

        onBoundsChange({
            lat_min: bounds.getSouth(),
            lat_max: bounds.getNorth(),
            long_min: bounds.getEast(),
            long_max: bounds.getWest(),
        });
    }

    useEffect(() => {
        updateBounds();
    }, []);

    return null;
}


// default map views + store + load from localstorage
export const DEFAULT_CENTER = [1.2595764399413216, 103.8335830126783];
const DEFAULT_ZOOM = 14;

export function MapStateSaver() {
  useMapEvents({
    moveend: (e) => {
      const map = e.target;
      const center = map.getCenter();
      const zoom = map.getZoom();

      localStorage.setItem('mapCenter', JSON.stringify([center.lat, center.lng]));
      localStorage.setItem('mapZoom', JSON.stringify(zoom));
    },
  });
  return null;
}

export const getMapCenter = () => {
  try {
    const saved = localStorage.getItem('mapCenter');
    return saved ? JSON.parse(saved) : DEFAULT_CENTER;
  } catch (error) {
    return DEFAULT_CENTER;
  }
};

export const getMapZoom = () => {
  try {
    const saved = localStorage.getItem('mapZoom');
    return saved ? JSON.parse(saved) : DEFAULT_ZOOM;
  } catch (error) {
    return DEFAULT_ZOOM;
  }
};
