# backend/app/modules/alerts/context_builder.py

'''
Context Builder for Alert Engine
Defines standardized context structures for different alert types
'''

from typing import Dict, Any, List

def build_geofence_context(vessel_mmsi: str, geofence_id: int, event: str) -> Dict[str, Any]:
    '''
    Build context for geofence alerts
    '''
    return {
        "type": "geofence",
        "vessel_mmsi": vessel_mmsi,
        "geofence_id": geofence_id,
        "event": event
    }
