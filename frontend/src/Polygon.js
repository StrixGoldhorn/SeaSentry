import { Rectangle, Polygon } from 'react-leaflet';

export function PolygonOverlay ({ coords, color }) {

    const polyOptions = {
        color: `${color}`,
        weight: 3,
        opacity: 0.3,
        fillColor: `${color}`,
        fillOpacity: 0.03
    }

    const polyBounds = coords.map(([lng, lat]) => [lat, lng]);

    return (
        <Polygon positions={polyBounds} pathOptions={polyOptions} />
    )
}







//DEPRECATED
// export function RectangleOverlay ({ bbox, color }) {

//     const rectOptions = {
//         color: `${color}`,
//         weight: 3,
//         opacity: 0.3,
//         fillColor: `${color}`,
//         fillOpacity: 0.03
//     }

//     const rectBounds = [
//         [bbox.lat_min, bbox.long_min],
//         [bbox.lat_max, bbox.long_max]
//     ]

//     return (
//         <Rectangle bounds={rectBounds} pathOptions={rectOptions} />
//     )
// }
