import { Rectangle } from 'react-leaflet';

export function rectangleOverlay (bbox) {

    
    
    const rectOptions = {
        color: 'blue',
        weight: 3,
        opacity: 0.7,
        fillColor: 'blue',
        fillOpacity: 0.05
    }

    const rectBounds = [
        [bbox.lat_min, bbox.long_min],
        [bbox.lat_max, bbox.long_max]
    ]

    return (
        <Rectangle bounds={rectBounds} pathOptions={rectOptions} />
    )
}