# API Documentation
All APIs are requested on localhost port 5000. Otherwise, CORS only allowed on http://localhost:3000 and http://127.0.0.1:3000 for the web application.

Fields are compulsory unless otherwise stated

## Table of Contents
- [API Documentation](#api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Vessels](#vessels)
    - [GET `/api/v1/vessels/bbox`](#get-apiv1vesselsbbox)
  - [AOIs](#aois)
    - [GET `/api/v1/aois/get/all`](#get-apiv1aoisgetall)
    - [POST `/api/v1/aois/add/box`](#post-apiv1aoisaddbox)
    - [POST `/api/v1/aois/add/polygon`](#post-apiv1aoisaddpolygon)
  - [Geofences](#geofences)
    - [GET `/api/v1/geofences/get/all`](#get-apiv1geofencesgetall)
    - [POST `/api/v1/geofences/add/box`](#post-apiv1geofencesaddbox)
    - [POST `/api/v1/geofences/add/polygon`](#post-apiv1geofencesaddpolygon)
  - [Alerts](#alerts)
    - [GET `/api/v1/alerts/history/all`](#get-apiv1alertshistoryall)
    - [GET `/api/v1/alerts/history/unread`](#get-apiv1alertshistoryunread)



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



## AOIs

### GET `/api/v1/aois/get/all`

Summary: Query for all AOIs

Returns:

- 200 with JSON of all AOIs

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



## Geofences

### GET `/api/v1/geofences/get/all`

Summary: Query for all AOIs

Returns:

- 200 with JSON of all AOIs

- 500 if internal server error

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

## Alerts

### GET `/api/v1/alerts/history/all`

Summary: Returns history of all alerts, both read and unread

Returns:

- 200 with JSON with history of all alerts

- 500 if internal server error

### GET `/api/v1/alerts/history/unread`

Summary: Returns history of all unread alerts

Returns:

- 200 with JSON with history of all unread alerts

- 500 if internal server error
