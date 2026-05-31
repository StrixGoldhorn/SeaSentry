import { Rectangle } from 'react-leaflet';

export function rectangleOverlay (bbox) {

    
    
    const rectOptions = {
        color: 'green',
        weight: 3,
        opacity: 0.3,
        fillColor: 'green',
        fillOpacity: 0.03
    }

    const rectBounds = [
        [bbox.lat_min, bbox.long_min],
        [bbox.lat_max, bbox.long_max]
    ]

    return (
        <Rectangle bounds={rectBounds} pathOptions={rectOptions} />
    )
}