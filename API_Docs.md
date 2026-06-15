# API Documentation
All APIs are requested on localhost port 5000. Otherwise, CORS only allowed on http://localhost:3000 and http://127.0.0.1:3000 for the web application.

Fields are compulsory unless otherwise stated

## Table of Contents
- [API Documentation](#api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Vessels](#vessels)
    - [GET `/api/v1/vessels/bbox`](#get-apiv1vesselsbbox)
    - [GET `/api/v1/vessels/<vessel_data_id>`](#get-apiv1vesselsvessel_data_id)
  - [AOIs](#aois)
    - [GET `/api/v1/aois/get/all`](#get-apiv1aoisgetall)
    - [GET `/api/v1/aois/<aoi_id>`](#get-apiv1aoisaoi_id)
    - [POST `/api/v1/aois/add/box`](#post-apiv1aoisaddbox)
    - [POST `/api/v1/aois/add/polygon`](#post-apiv1aoisaddpolygon)
    - [POST/PATCH `/api/v1/aois/<aoi_id>/update`](#postpatch-apiv1aoisaoi_idupdate)
  - [Geofences](#geofences)
    - [GET `/api/v1/geofences/get/all`](#get-apiv1geofencesgetall)
    - [GET `/api/v1/geofences/<geofence_id>`](#get-apiv1geofencesgeofence_id)
    - [POST `/api/v1/geofences/add/box`](#post-apiv1geofencesaddbox)
    - [POST `/api/v1/geofences/add/polygon`](#post-apiv1geofencesaddpolygon)
    - [POST/PATCH `/api/v1/geofences/<geofence_id>/update`](#postpatch-apiv1geofencesgeofence_idupdate)
  - [Alert History](#alert-history)
    - [GET `/api/v1/alerts/history/all`](#get-apiv1alertshistoryall)
    - [GET `/api/v1/alerts/history/unread`](#get-apiv1alertshistoryunread)
    - [POST `/api/v1/alerts/history/<alert_history_id>/mark/read`](#post-apiv1alertshistoryalert_history_idmarkread)
    - [POST `/api/v1/alerts/history/<alert_history_id>/mark/unread`](#post-apiv1alertshistoryalert_history_idmarkunread)
  - [Alert Rules](#alert-rules)
    - [GET `/api/v1/alerts/rule/all`](#get-apiv1alertsruleall)
    - [POST `/api/v1/alerts/rule/add`](#post-apiv1alertsruleadd)



## Vessels

### GET `/api/v1/vessels/bbox`

Summary: Query latest vessel positions within a bounding box

Returns:

- 200 with JSON with latest vessel location and details

- 400 if missing fields

- 500 if internal server error

Query Params:

- lat_min, lat_max, long_min, long_max: float (bounding box)

- time_within: int (optional, time in seconds, default 24hrs ie 60 * 60 * 24)

- limit: int (optional, default 50, max 1000)

E.g. `/api/v1/vessels/bbox?lat_min=1.2535&lat_max=1.2664&long_min=103.8233&long_max=103.8559&limit=25&time_within=670`

This will return the 25 latest vessel locations with its corresponding unique vessels within the given area in the past 670 seconds.

### GET `/api/v1/vessels/<vessel_data_id>`

Summary: Query for vessel data with given vessel_data_id

Returns:

- 200 with details of vessel

- 400 if missing fields

- 500 if internal server error

## AOIs

### GET `/api/v1/aois/get/all`

Summary: Query for all AOIs

Returns:

- 200 with JSON of all AOIs

- 500 if internal server error

### GET `/api/v1/aois/<aoi_id>`

Summary: Query for AOI with given aoi_id

Returns:

- 200 with details of AOI

- 404 if AOI with aoi_id does not exist

- 500 if internal server error

### POST `/api/v1/aois/add/box`

Summary: Adds specified bounding box.

Returns:

- 201 if successfully added

- 400 if missing fields

- 403 if name already exsts

- 500 if internal server error

Query Params:

- lat_min, lat_max, long_min, long_max: float (bounding box)

- name: str (name of AOI)

- desc: str (optional, description of AOI)

### POST `/api/v1/aois/add/polygon`

Summary: Adds specified bounding polygon.

Returns:

- 201 if successfully added

- 400 if missing fields

- 403 if name already exsts

- 500 if internal server error

Query Params:

- coords: [[long1, lat1], [long2, lat2], [long3, lat3], ..., [long1, lat1]] (polygon bounding fence. last coords should be same as first coords. else it will automatically close the loop, which may lead to unexpected behaviours.)

- name: str (name of AOI)

- desc: str (optional, description of AOI)

### POST/PATCH `/api/v1/aois/<aoi_id>/update`

Summary: Updates an existing Area of Interest. Supports partial updates.

Query Params (all optional, but at least one required):
- name: str (new name of AOI)

- desc: str (new description of AOI)

- coords: str (JSON array of [[long, lat], ...] for polygon update)

- lat_min, lat_max, long_min, long_max: float (for bounding box update)
    
Returns:

- 200 if successfully updated

- 400 if missing/malformed fields

- 404 if AOI with id does not exist

- 500 if internal server error

## Geofences

### GET `/api/v1/geofences/get/all`

Summary: Query for all AOIs

Returns:

- 200 with JSON of all AOIs

- 500 if internal server error

### GET `/api/v1/geofences/<geofence_id>`

Summary: Query for Geofence with given geofence_id

Returns:

- 200 with details of Geofence

- 404 if Geofence with geofence_id does not exist

- 500 if internal server error
- 
### POST `/api/v1/geofences/add/box`

Summary: Adds specified bounding box.

Returns:

- 201 if successfully added

- 400 if missing fields

- 403 if name already exsts

- 500 if internal server error

Query Params:

- lat_min, lat_max, long_min, long_max: float (bounding box)

- name: str (name of geofence)

- desc: str (optional, description of geofence)

### POST `/api/v1/geofences/add/polygon`

Summary: Adds specified bounding polygon.

Returns:

- 201 if successfully added

- 400 if missing fields

- 403 if name already exsts
- 
- 500 if internal server error

Query Params:

- coords: [[long1, lat1], [long2, lat2], [long3, lat3], ..., [long1, lat1]] (polygon bounding fence. last coords should be same as first coords. else it will automatically close the loop, which may lead to unexpected behaviours.)

- name: str (name of geofence)

- desc: str (optional, description of geofence)

### POST/PATCH `/api/v1/geofences/<geofence_id>/update`

Summary: Updates an existing Geofence. Supports partial updates.

Query Params (all optional, but at least one required):
- name: str (new name of Geofence)

- desc: str (new description of Geofence)

- coords: str (JSON array of [[long, lat], ...] for polygon update)

- lat_min, lat_max, long_min, long_max: float (for bounding box update)
    
Returns:

- 200 if successfully updated

- 400 if missing/malformed fields

- 404 if Geofence with id does not exist

- 500 if internal server error

## Alert History

### GET `/api/v1/alerts/history/all`

Summary: Returns history of all alerts, both read and unread

Query Params (all optional):
- start_time: ISO format datetime string (e.g., 2023-10-27T10:00:00)
- end_time: ISO format datetime string (e.g., 2023-10-28T10:00:00)
- limit: integer, max number of records to return (e.g., 50)
- offset: integer, number of records to skip for pagination (e.g., 0)

Returns:

- 200 with JSON with history of all alerts

- 400 if malformed fields

- 500 if internal server error

### GET `/api/v1/alerts/history/unread`

Summary: Returns history of all unread alerts

Query Params (all optional):
- start_time: ISO format datetime string (e.g., 2023-10-27T10:00:00)
- end_time: ISO format datetime string (e.g., 2023-10-28T10:00:00)
- limit: integer, max number of records to return (e.g., 50)
- offset: integer, number of records to skip for pagination (e.g., 0)

Returns:

- 200 with JSON with history of all unread alerts

- 400 if malformed fields

- 500 if internal server error

### POST `/api/v1/alerts/history/<alert_history_id>/mark/read`

Summary: Marks the given alert history as read

Returns:

- 200 if successfully marked as read

- 404 if no such alert history with given id exists

- 500 if internal server error

### POST `/api/v1/alerts/history/<alert_history_id>/mark/unread`

Summary: Marks the given alert history as unread

Returns:

- 200 if successfully marked as unread

- 404 if no such alert history with given id exists

- 500 if internal server error

## Alert Rules

### GET `/api/v1/alerts/rule/all`

Summary: Returns all alert rules

Returns:

- 200 with JSON with all alert rules

- 500 if internal server error

### POST `/api/v1/alerts/rule/add`

Summary: Adds a new custom alert rule

Query param:

JSON with the keys:
- "name": name of alert, must be unique
- "desc" (optional): description of alert
- "params": params defining the alert rule

Eg. for a single rule,
```JSON
{
  "name": "name of alert",
  "description": "description of alert",
  "params": {
    "field": "speed",
    "operator": ">",
    "value": 10.0
  }
}
```

Eg. for multiple/combined rules,
```JSON
{
  "name": "name of alert",
  "description": "description of alert",
  "params": {
    "rules": [
      {
        "field": "inside_geofence",
        "value": true,
        "operator": "=",
        "valueGeofenceid": 3
      },
      {
        "field": "enter_geofence",
        "value": true,
        "operator": "=",
        "valueGeofenceid": 3
      },
      {
        "field": "exit_geofence",
        "value": true,
        "operator": "=",
        "valueGeofenceid": 3
      }
    ],
    "combinator": "or"
  }
}
```

Allowed fields
```
shipname
shiptype
mmsi
speed
proximity_to_shiptype
inside_geofence
enter_geofence
exit_geofence
is_vessel_of_interes
```

Allowed operators
```
=
!=
>
<
>=
<=
LIKE
```

Allowed combinators
```
and
or
not
```

Returns:

- 201 with the new alert_rule_id if inserted successfully

- 400 if missing/malformed fields

- 500 if internal server error
