# API Documentation
All APIs are requested on localhost port 5000. Otherwise, CORS only allowed on http://localhost:3000 and http://127.0.0.1:3000 for the web application.

Fields are compulsory unless otherwise stated

## Table of Contents
- [API Documentation](#api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Vessels](#vessels)
    - [GET `/api/v1/vessels/bbox`](#get-apiv1vesselsbbox)
    - [GET `/api/v1/vessels/<vessel_data_id>`](#get-apiv1vesselsvessel_data_id)
    - [POST/PATCH `/api/v1/vessels/<vessel_data_id>/update`](#postpatch-apiv1vesselsvessel_data_idupdate)
    - [GET `/api/v1/vessels/history`](#get-apiv1vesselshistory)
  - [Vessel of Interest](#vessel-of-interest)
    - [GET `/api/v1/vessel_of_interest/get/all`](#get-apiv1vessel_of_interestgetall)
    - [GET `/api/v1/vessel_of_interest/<vessel_of_interest_id>`](#get-apiv1vessel_of_interestvessel_of_interest_id)
    - [POST `/api/v1/vessel_of_interest/add`](#post-apiv1vessel_of_interestadd)
    - [POST/PATCH `/api/v1/vessel_of_interest/<vessel_of_interest_id>/update`](#postpatch-apiv1vessel_of_interestvessel_of_interest_idupdate)
    - [DELETE `/api/v1/vessel_of_interest/<vessel_of_interest_id>/delete`](#delete-apiv1vessel_of_interestvessel_of_interest_iddelete)
  - [AOIs](#aois)
    - [GET `/api/v1/aois/get/all`](#get-apiv1aoisgetall)
    - [GET `/api/v1/aois/<aoi_id>`](#get-apiv1aoisaoi_id)
    - [POST `/api/v1/aois/add/box`](#post-apiv1aoisaddbox)
    - [POST `/api/v1/aois/add/polygon`](#post-apiv1aoisaddpolygon)
    - [POST/PATCH `/api/v1/aois/<aoi_id>/update`](#postpatch-apiv1aoisaoi_idupdate)
    - [DELETE `/api/v1/aois/<aoi_id>/delete`](#delete-apiv1aoisaoi_iddelete)
  - [Geofences](#geofences)
    - [GET `/api/v1/geofences/get/all`](#get-apiv1geofencesgetall)
    - [GET `/api/v1/geofences/<geofence_id>`](#get-apiv1geofencesgeofence_id)
    - [POST `/api/v1/geofences/add/box`](#post-apiv1geofencesaddbox)
    - [POST `/api/v1/geofences/add/polygon`](#post-apiv1geofencesaddpolygon)
    - [POST/PATCH `/api/v1/geofences/<geofence_id>/update`](#postpatch-apiv1geofencesgeofence_idupdate)
    - [DELETE `/api/v1/geofences/<geofence_id>/delete`](#delete-apiv1geofencesgeofence_iddelete)
  - [Alert History](#alert-history)
    - [GET `/api/v1/alerts/history/all`](#get-apiv1alertshistoryall)
    - [GET `/api/v1/alerts/history/unread`](#get-apiv1alertshistoryunread)
    - [POST `/api/v1/alerts/history/<alert_history_id>/mark/read`](#post-apiv1alertshistoryalert_history_idmarkread)
    - [POST `/api/v1/alerts/history/<alert_history_id>/mark/unread`](#post-apiv1alertshistoryalert_history_idmarkunread)
  - [Alert Rules](#alert-rules)
    - [GET `/api/v1/alerts/rule/all`](#get-apiv1alertsruleall)
    - [POST `/api/v1/alerts/rule/add`](#post-apiv1alertsruleadd)
    - [POST `/api/v1/alerts/rule/<alert_rule_id>/update`](#post-apiv1alertsrulealert_rule_idupdate)
    - [POST `/api/v1/alerts/rule/<alert_rule_id>/mark/disable`](#post-apiv1alertsrulealert_rule_idmarkdisable)
    - [POST `/api/v1/alerts/rule/<alert_rule_id>/mark/enable`](#post-apiv1alertsrulealert_rule_idmarkenable)
    - [DELETE `/api/v1/alerts/rule/<alert_rule_id>/delete`](#delete-apiv1alertsrulealert_rule_iddelete)
- [Rule Configuration](#rule-configuration)
  - [Explanation](#explanation)
  - [Fields and Operators](#fields-and-operators)
    - [shipname](#shipname)
    - [shiptype](#shiptype)
    - [mmsi](#mmsi)
    - [speed](#speed)
    - [proximity\_to\_shiptype](#proximity_to_shiptype)
    - [inside\_geofence](#inside_geofence)
    - [enter\_geofence](#enter_geofence)
    - [exit\_geofence](#exit_geofence)
    - [is\_vessel\_of\_interest](#is_vessel_of_interest)
  - [Using Combinators](#using-combinators)
  - [Nested Rules](#nested-rules)



## Vessels

### GET `/api/v1/vessels/bbox`

Summary: Query latest vessel positions within a bounding box

Query Params:
- lat_min, lat_max, long_min, long_max: float (bounding box)
- time_within: int (optional, time in seconds, default 24hrs ie 60 * 60 * 24)
- limit: int (optional, default 50, max 1000)

E.g. `/api/v1/vessels/bbox?lat_min=1.2535&lat_max=1.2664&long_min=103.8233&long_max=103.8559&limit=25&time_within=670`

This will return the 25 latest vessel locations with its corresponding unique vessels within the given area in the past 670 seconds.

Returns:
- 200 with JSON with latest vessel location and details
- 400 if missing fields
- 500 if internal server error

### GET `/api/v1/vessels/<vessel_data_id>`

Summary: Query for vessel data with given vessel_data_id

Returns:
- 200 with details of vessel
- 400 if missing fields
- 500 if internal server error

### POST/PATCH `/api/v1/vessels/<vessel_data_id>/update`

Summary: Updates an existing Vessel. Supports partial updates.

Request Body (all optional, but at least one required):
- ship_name: str (new ship name of Vessel)
- ship_type: str (new ship type of Vessel)
- flag: str (new flag of Vessel)
- length_meters: int (new length (in meters) of Vessel)
- beam_meters: int (new beam (in meters) of Vessel)
- user_tags: array of string (new user tags for Vessel)
    
Returns:
- 200 if successfully updated
- 400 if missing/malformed fields
- 404 if Vessel with id does not exist
- 500 if internal server error

### GET `/api/v1/vessels/history`

Summary: Query historical vessel positions within a bounding box and time range. Streams exports to JSON, GeoJSON, or CSV to prevent memory overload on large responses.

Query Params:
- lat_min, lat_max, long_min, long_max: float (bounding box)
- start_time: str (ISO datetime string, e.g., '2023-10-01T12:00:00Z')
- end_time: str (ISO datetime string, e.g., '2023-10-02T12:00:00Z')
- format: str (optional, 'json', 'geojson', or 'csv', default 'json')

Returns:
- 200 with JSON, GeoJSON, or CSV containing historical vessel locations and details
- 400 if missing/malformed fields
- 500 if internal server error

## Vessel of Interest

### GET `/api/v1/vessel_of_interest/get/all`

Summary: Query for all vessels of interest

Returns:
- 200 with JSON of all vessels of interest
- 500 if internal server error

### GET `/api/v1/vessel_of_interest/<vessel_of_interest_id>`

Summary: Query for vessel of interest with given vessel_of_interest_id

Returns:
- 200 with details of vessel of interest
- 404 if vessel of interest with vessel_of_interest_id does not exist
- 500 if internal server error

### POST `/api/v1/vessel_of_interest/add`

Summary: Adds specified vessel of interest

Request Body:

**Note**: Either MMSI, or IMO, or both MMSI and IMO must be present.
- name: str (user-defined name for the vessel of interest)
- desc: str (optional, description of the vessel of interest)
- mmsi: str (MMSI of the vessel of interest)
- imo: str (IMO of the vessel of interest)

Returns:
- 201 if successfully added
- 400 if missing/malformed fields
- 403 if name already exists
- 500 if internal server error

### POST/PATCH `/api/v1/vessel_of_interest/<vessel_of_interest_id>/update`

Summary: Updates an existing Vessel of Interest. Supports partial updates.

Request Body (all optional, but at least one required):

**Note**: Either MMSI, or IMO, or both MMSI and IMO must be present in the database after update.
- desc_name: str (new user-defined name of Vessel of Interest)
- desc: str (new description of Vessel of Interest)
- mmsi: str (new mmsi of Vessel of Interest)
- imo: str (new imo of Vessel of Interest)
    
Returns:
- 200 if successfully updated
- 400 if missing/malformed fields
- 403 if new user-defined name already exists
- 404 if Vessel of Interest with id does not exist
- 500 if internal server error

### DELETE `/api/v1/vessel_of_interest/<vessel_of_interest_id>/delete`

Summary: Deletes an existing Vessel of Interest.

Query Param:
- voi_name: Name of the Vessel of Interest to be deleted.

**Note**: The above is done solely to ensure that the user does not accidentally delete the wrong Vessel of Interest.
    
Returns:
- 200 if successfully deleted
- 400 if missing/malformed fields
- 403 if provided voi_name is incorrect
- 404 if Vessel of Interest with id does not exist
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

Request Body:
- lat_min, lat_max, long_min, long_max: float (bounding box)
- name: str (name of AOI)
- desc: str (optional, description of AOI)

Returns:
- 201 if successfully added
- 400 if missing fields
- 403 if name already exists
- 500 if internal server error

### POST `/api/v1/aois/add/polygon`

Summary: Adds specified bounding polygon.

Request Body:
- coords: [[long1, lat1], [long2, lat2], [long3, lat3], ..., [long1, lat1]] (polygon bounding fence. last coords should be same as first coords. else it will automatically close the loop, which may lead to unexpected behaviours.)
- name: str (name of AOI)
- desc: str (optional, description of AOI)

Returns:
- 201 if successfully added
- 400 if missing fields
- 403 if name already exists
- 500 if internal server error

### POST/PATCH `/api/v1/aois/<aoi_id>/update`

Summary: Updates an existing Area of Interest. Supports partial updates.

Request Body (all optional, but at least one required):
- name: str (new name of AOI)
- desc: str (new description of AOI)
- coords: str (JSON array of [[long, lat], ...] for polygon update)
- lat_min, lat_max, long_min, long_max: float (for bounding box update)
    
Returns:
- 200 if successfully updated
- 400 if missing/malformed fields
- 404 if AOI with id does not exist
- 500 if internal server error

### DELETE `/api/v1/aois/<aoi_id>/delete`

Summary: Deletes an existing Area of Interest.

Query Param:
- aoi_name: Name of the AOI to be deleted.

**Note**: The above is done solely to ensure that the user does not accidentally delete the wrong AOI.
    
Returns:
- 200 if successfully deleted
- 400 if missing/malformed fields
- 403 if provided aoi_name is incorrect
- 404 if AOI with id does not exist
- 500 if internal server error

## Geofences

### GET `/api/v1/geofences/get/all`

Summary: Query for all Geofences

Returns:
- 200 with JSON of all Geofences
- 500 if internal server error

### GET `/api/v1/geofences/<geofence_id>`

Summary: Query for Geofence with given geofence_id

Returns:
- 200 with details of Geofence
- 404 if Geofence with geofence_id does not exist
- 500 if internal server error

### POST `/api/v1/geofences/add/box`

Summary: Adds specified bounding box.

Request Body:
- lat_min, lat_max, long_min, long_max: float (bounding box)
- name: str (name of geofence)
- desc: str (optional, description of geofence)

Returns:
- 201 if successfully added
- 400 if missing fields
- 403 if name already exists
- 500 if internal server error

### POST `/api/v1/geofences/add/polygon`

Summary: Adds specified bounding polygon.

Request Body:
- coords: [[long1, lat1], [long2, lat2], [long3, lat3], ..., [long1, lat1]] (polygon bounding fence. last coords should be same as first coords. else it will automatically close the loop, which may lead to unexpected behaviours.)
- name: str (name of geofence)
- desc: str (optional, description of geofence)

Returns:
- 201 if successfully added
- 400 if missing fields
- 403 if name already exists
- 500 if internal server error

### POST/PATCH `/api/v1/geofences/<geofence_id>/update`

Summary: Updates an existing Geofence. Supports partial updates.

Request Body (all optional, but at least one required):
- name: str (new name of Geofence)
- desc: str (new description of Geofence)
- coords: str (JSON array of [[long, lat], ...] for polygon update)
- lat_min, lat_max, long_min, long_max: float (for bounding box update)
    
Returns:
- 200 if successfully updated
- 400 if missing/malformed fields
- 404 if Geofence with id does not exist
- 500 if internal server error

### DELETE `/api/v1/geofences/<geofence_id>/delete`

Summary: Deletes an existing Geofence.

Query Param:
- geofence_name: Name of the Geofence to be deleted.

**Note**: The above is done solely to ensure that the user does not accidentally delete the wrong Geofence.
    
Returns:
- 200 if successfully deleted
- 400 if missing/malformed fields
- 403 if provided geofence_name is incorrect
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

Request Body:

JSON with the keys:
- "name": name of alert, must be unique
- "description" (optional): description of alert
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

Refer to Rule Configuration below for all allowed fields, operators, combinators.

Returns:
- 201 with the new alert_rule_id if inserted successfully
- 400 if missing/malformed fields
- 500 if internal server error

### POST `/api/v1/alerts/rule/<alert_rule_id>/update`

Summary: Updates an existing alert rule. Supports partial updates.

Request Body:

JSON with the keys:
- "name": name of alert, must be unique
- "description" (optional): description of alert
- "params": params defining the alert rule

Returns:
- 200 if successfully updated
- 400 if missing/malformed fields
- 404 if alert rule with id does not exist
- 500 if internal server error

### POST `/api/v1/alerts/rule/<alert_rule_id>/mark/disable`

Summary: Marks the given alert rule as disabled

Returns:
- 200 if successfully marked as disabled
- 404 if no such alert rule with given id exists
- 500 if internal server error

### POST `/api/v1/alerts/rule/<alert_rule_id>/mark/enable`

Summary: Marks the given alert rule as enabled

Returns:
- 200 if successfully marked as enabled
- 404 if no such alert rule with given id exists
- 500 if internal server error

### DELETE `/api/v1/alerts/rule/<alert_rule_id>/delete`

Summary: Deletes an existing alert rule

Query Param:
- alert_rule_name: Name of the alert rule to be deleted.

**Note**: The above is done solely to ensure that the user does not accidentally delete the wrong alert rule.
    
Returns:
- 200 if successfully deleted
- 400 if missing/malformed fields
- 403 if provided alert_rule_name is incorrect
- 404 if alert rule with id does not exist
- 500 if internal server error


# Rule Configuration

## Explanation

Rules are implemented as an [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree), with the leaves being a condition for a field. Non-leaf nodes are combinators, ie `and`, `or`, `not`. This allows combining different conditions together, and is functionally complete (in terms of boolean logic).

Fields have limited operators they have access to.

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
is_vessel_of_interest
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

## Fields and Operators
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
is_vessel_of_interest
```

### shipname
Allowed operators
- `=`: Strict equality check
- `LIKE`: Will execute a wildcard match

Examples
```
{
  "field": "shipname",
  "operator": "LIKE",
  "value": "MPA"
}
```
```
{
  "field": "shipname",
  "operator": "=",
  "value": "SCDF"
}
```

### shiptype
Allowed operators
- `=`: Checks if shiptype is the same as user provided
- `!=`: Checks if shiptype is different from the one user provided

Examples
```
{
  "field": "shiptype",
  "operator": "=",
  "value": "Tug"
}
```
```
{
  "field": "shiptype",
  "operator": "!=",
  "value": "Cargo"
}
```

### mmsi
Allowed operators
- `=`: Checks if MMSI of vessels is the same as the one provided

Example
```
{
  "field": "mmsi",
  "operator": "=",
  "value": "123456789"
}
```

### speed
Allowed operators
- `>`: Checks if speed of vessel recorded is strictly more than the one provided
- `<`: Checks if speed of vessel recorded is strictly less than the one provided
- `>=`: Checks if speed of vessel recorded is more than or equals to the one provided
- `<=`: Checks if speed of vessel recorded is less than or equals to the one provided
- `=`: Checks if speed of vessel recorded is strictly equals to the one provided

Example
```
{
  "field": "speed",
  "operator": ">=",
  "value": 6.7
}
```

### proximity_to_shiptype
Requires a special field, `valueShiptype`.

Will return any ships within `value` meters of any `valueShiptype` ship.

Operator can be any (will be ignored).

Example
```
{
  "field": "proximity_to_shiptype",
  "operator": true,
  "value": 100,
  "valueShiptype": "Cargo"
}
```

### inside_geofence
Requires a special field, `valueGeofenceid`.

Will return any ships within geofence with `valueGeofenceid`.

Operator and value can be any (will be ignored).

Example
```
{
  "field": "inside_geofence",
  "operator": "=",
  "value": true,
  "valueGeofenceid": 3
}
```

### enter_geofence
Requires a special field, `valueGeofenceid`.

Will return any ships entering geofence with `valueGeofenceid`.

Operator and value can be any (will be ignored).

Example
```
{
  "field": "enter_geofence",
  "operator": "=",
  "value": true,
  "valueGeofenceid": 3
}
```

### exit_geofence
Requires a special field, `valueGeofenceid`.

Will return any ships exiting geofence with `valueGeofenceid`.

Operator and value can be any (will be ignored).

Example
```
{
  "field": "exit_geofence",
  "operator": "=",
  "value": true,
  "valueGeofenceid": 3
}
```

### is_vessel_of_interest
Will return true if vessel is a user-defined vessel of interest.

Generally used with combinators.

Operator and value can be any (will be ignored).

Example
```
{
  "field": "is_vessel_of_interest",
  "operator": "=",
  "value": "abc"
}
```

## Using Combinators
Combinators can be used to combine singular rules.

Available combinators are `and`, `or`, `not`.

For example, the code below will be evaluated as true if any a vessel is inside, or entering, or exiting geofecnce 3.

```
"combinator": "or",
"rules": [
    {
        "field": "inside_geofence",
        "operator": "=",
        "value": true,
        "valueGeofenceid": 3
    },
    {
        "field": "enter_geofence",
        "operator": "=",
        "value": true,
        "valueGeofenceid": 3
    },
    {
        "field": "exit_geofence",
        "operator": "=",
        "value": true,
        "valueGeofenceid": 3
    }
]
```

## Nested Rules
Combinators can be nested within combinators.

For example, the rule below evaluates true if `(vessel is NOT inside geofence 1) AND (shipname is like MPA OR shipname is like SCDF)`

```
"rules": [
  {
    "combinator": "not",
    "rules": [
      {
        "field": "inside_geofence",
        "operator": "=",
        "value": true,
        "valueGeofenceid": 1
      }
    ]
  },
  {
    "rules": [
      {
        "field": "shipname",
        "value": "MPA",
        "operator": "LIKE"
      },
      {
        "field": "shipname",
        "value": "SCDF",
        "operator": "LIKE"
      }
    ],
    "combinator": "or"
  }
],
"combinator": "and"
```
