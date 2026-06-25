const config = require('./config');

//FormData helper function
function appendIfNotNull(formData, key, value) {
    if (value !== null && value !== undefined) {
        formData.append(key, value);
    }
}

//VESSELS
//Query latest vessel positions within a bounding box
export async function get_ships_on_screen({lat_min, lat_max, long_min, long_max, limit = null, time_within = null}) {
    if (lat_min == null || lat_max == null || long_min == null || long_max == null) {
        return null;
    }


    let url = config.api_url + `/api/v1/vessels/bbox?`
    +`lat_min=${lat_min}&lat_max=${lat_max}&`
    +`long_min=${long_min}&long_max=${long_max}`;

    // PLEASE check if these 2 work properly, with the wonky true/false js stuff
    if (limit !== null) {
        url = url + `&limit=${limit}`;
    }

    if (time_within !== null) {
        url = url + `&time_within=${time_within}`;
    }

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Query for vessel data with given vessel_data_id
export async function get_ship_using_data_id({vessel_data_id}) {
    if (vessel_data_id == null) {
        return null;
    }


    let url = config.api_url + `/api/v1/vessels/`
    +`${vessel_data_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Updates an existing Vessel. Supports partial updates.
export async function update_ship_using_data_id({
    vessel_data_id,
    ship_name = null,
    ship_type = null,
    flag = null,
    length_meters = null,
    beam_meters = null,
    user_tags = null
}) {

    if (
        ship_name == null &&
        ship_type == null &&
        flag == null &&
        length_meters == null &&
        beam_meters == null &&
        user_tags == null
    ) {
        return null;
    }

    if (vessel_data_id == null) {
        return null;
    }

    const formData = new FormData();

    appendIfNotNull(formData, "ship_name", ship_name);
    appendIfNotNull(formData, "ship_type", ship_type);
    appendIfNotNull(formData, "flag", flag);
    appendIfNotNull(formData, "length_meters", length_meters);
    appendIfNotNull(formData, "beam_meters", beam_meters);

    if (user_tags !== null) {
        formData.append("user_tags", JSON.stringify(user_tags));
    }

    return await fetch(
        config.api_url + `/api/v1/vessels/${vessel_data_id}/update`,
        {
            method: "PATCH",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//VESSELS OF INTEREST
//Query for all vessels of interest
export async function get_all_VOI() {

    let url = config.api_url + `/api/v1/vessel_of_interest/get/all`
    
    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Query for vessel of interest with given vessel_of_interest_id
export async function get_VOI_using_id({voi_id}) {
    if (voi_id == null) {
        return null;
    }


    let url = config.api_url + `/api/v1/vessel_of_interest/`
    +`${voi_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified vessel of interest
export async function add_VOI({ name, desc = null, mmsi, imo }) {

    if (name == null) return null;
    if (mmsi == null && imo == null) return null;

    const formData = new FormData();

    formData.append("name", name);
    appendIfNotNull(formData, "desc", desc);
    appendIfNotNull(formData, "mmsi", mmsi);
    appendIfNotNull(formData, "imo", imo);

    return await fetch(
        config.api_url + `/api/v1/vessel_of_interest/add`,
        {
            method: "POST",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//AOI
//Query for all AOIs
export async function get_all_AOI() {

    let url = config.api_url + `/api/v1/aois/get/all`
    
    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Query for AOI with given aoi_id
export async function get_AOI_using_id({aoi_id}) {
    if (aoi_id == null) {
        return null;
    }


    let url = config.api_url + `/api/v1/aois/`
    +`${aoi_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified bounding box.
export async function add_box_AOI({
    lat_min,
    lat_max,
    long_min,
    long_max,
    name,
    desc = null
}) {

    if (
        lat_min == null ||
        lat_max == null ||
        long_min == null ||
        long_max == null ||
        name == null
    ) {
        return null;
    }

    const formData = new FormData();

    formData.append("lat_min", lat_min);
    formData.append("lat_max", lat_max);
    formData.append("long_min", long_min);
    formData.append("long_max", long_max);
    formData.append("name", name);

    appendIfNotNull(formData, "desc", desc);

    return await fetch(
        config.api_url + `/api/v1/aois/add/box`,
        {
            method: "POST",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Adds specified bounding polygon.
export async function add_poly_AOI({
    coords,
    name,
    desc = null
}) {

    if (coords == null || name == null) {
        return null;
    }

    const formData = new FormData();

    formData.append(
        "coords",
        typeof coords === "string"
            ? coords
            : JSON.stringify(coords)
    );

    formData.append("name", name);

    appendIfNotNull(formData, "desc", desc);

    return await fetch(
        config.api_url + `/api/v1/aois/add/polygon`,
        {
            method: "POST",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Updates an existing Area of Interest. Supports partial updates.
export async function update_AOI({
    aoi_id,
    name = null,
    desc = null,
    coords = null,
    lat_min = null,
    lat_max = null,
    long_min = null,
    long_max = null
}) {

    if (aoi_id == null) return null;

    if (
        name == null &&
        desc == null &&
        coords == null &&
        lat_min == null &&
        lat_max == null &&
        long_min == null &&
        long_max == null
    ) {
        return null;
    }

    const formData = new FormData();

    appendIfNotNull(formData, "name", name);
    appendIfNotNull(formData, "desc", desc);

    if (coords !== null) {
        formData.append(
            "coords",
            typeof coords === "string"
                ? coords
                : JSON.stringify(coords)
        );
    }

    appendIfNotNull(formData, "lat_min", lat_min);
    appendIfNotNull(formData, "lat_max", lat_max);
    appendIfNotNull(formData, "long_min", long_min);
    appendIfNotNull(formData, "long_max", long_max);

    return await fetch(
        config.api_url + `/api/v1/aois/${aoi_id}/update`,
        {
            method: "PATCH",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Deletes an existing Area of Interest.
export async function delete_AOI({
    aoi_id,
    aoi_name
}) {

    if (aoi_id == null || aoi_name == null) {
        return null;
    }

    const url =
        config.api_url +
        `/api/v1/aois/${aoi_id}/delete?` + `aoi_name=${aoi_name}`;

    return await fetch(url, {
        method: "DELETE"
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}


//GEOFENCES
//Query for all Geofences
export async function get_all_geofences() {

    let url = config.api_url + `/api/v1/geofences/get/all`
    
    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Query for Query for Geofence with given geofence_id
export async function get_geofence_using_id({geofence_id}) {
    if (geofence_id == null) {
        return null;
    }


    let url = config.api_url + `/api/v1/geofences/`
    +`${geofence_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified bounding box.
export async function add_box_geofence({
    lat_min,
    lat_max,
    long_min,
    long_max,
    name,
    desc = null
}) {

    if (
        lat_min == null ||
        lat_max == null ||
        long_min == null ||
        long_max == null ||
        name == null
    ) {
        return null;
    }

    const formData = new FormData();

    formData.append("lat_min", lat_min);
    formData.append("lat_max", lat_max);
    formData.append("long_min", long_min);
    formData.append("long_max", long_max);
    formData.append("name", name);

    appendIfNotNull(formData, "desc", desc);

    return await fetch(
        config.api_url + `/api/v1/geofences/add/box`,
        {
            method: "POST",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Adds specified bounding polygon.
export async function add_poly_geofence({
    coords,
    name,
    desc = null
}) {

    if (coords == null || name == null) {
        return null;
    }

    const formData = new FormData();

    formData.append(
        "coords",
        typeof coords === "string"
            ? coords
            : JSON.stringify(coords)
    );

    formData.append("name", name);

    appendIfNotNull(formData, "desc", desc);

    return await fetch(
        config.api_url + `/api/v1/geofences/add/polygon`,
        {
            method: "POST",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Updates an existing geofence. Supports partial updates.
export async function update_geofence({
    geofence_id,
    name = null,
    desc = null,
    coords = null,
    lat_min = null,
    lat_max = null,
    long_min = null,
    long_max = null
}) {

    if (geofence_id == null) return null;

    if (
        name == null &&
        desc == null &&
        coords == null &&
        lat_min == null &&
        lat_max == null &&
        long_min == null &&
        long_max == null
    ) {
        return null;
    }

    const formData = new FormData();

    appendIfNotNull(formData, "name", name);
    appendIfNotNull(formData, "desc", desc);

    if (coords !== null) {
        formData.append(
            "coords",
            typeof coords === "string"
                ? coords
                : JSON.stringify(coords)
        );
    }

    appendIfNotNull(formData, "lat_min", lat_min);
    appendIfNotNull(formData, "lat_max", lat_max);
    appendIfNotNull(formData, "long_min", long_min);
    appendIfNotNull(formData, "long_max", long_max);

    return await fetch(
        config.api_url + `/api/v1/geofences/${geofence_id}/update`,
        {
            method: "PATCH",
            body: formData
        }
    )
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Deletes an existing Geofence.
export async function delete_geofence({
    geofence_id,
    geofence_name
}) {

    if (geofence_id == null || geofence_name == null) {
        return null;
    }


    const url =
        config.api_url +
        `/api/v1/geofences/${geofence_id}/delete?` + `geofence_name=${geofence_name}`;

    return await fetch(url, {
        method: "DELETE"
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}

//ALERT HISTORY
//Returns history of all alerts, both read and unread
export async function get_all_alert_history({
    start_time = null,
    end_time = null,
    limit = null,
    offset = null
}) {

    let url = config.api_url + "/api/v1/alerts/history/all?";
    let params = [];

    if (start_time !== null) {
        params.push(`start_time=${encodeURIComponent(start_time)}`);
    }

    if (end_time !== null) {
        params.push(`end_time=${encodeURIComponent(end_time)}`);
    }

    if (limit !== null) {
        params.push(`limit=${limit}`);
    }

    if (offset !== null) {
        params.push(`offset=${offset}`);
    }

    url += params.join("&");

    return await fetch(url)
        .then(res => res.json())
        .catch(err => console.error(err));
}


//Returns history of all unread alerts
export async function get_unread_alert_history({
    start_time = null,
    end_time = null,
    limit = null,
    offset = null
}) {

    let url = config.api_url + "/api/v1/alerts/history/unread?";
    let params = [];

    if (start_time !== null) {
        params.push(`start_time=${encodeURIComponent(start_time)}`);
    }

    if (end_time !== null) {
        params.push(`end_time=${encodeURIComponent(end_time)}`);
    }

    if (limit !== null) {
        params.push(`limit=${limit}`);
    }

    if (offset !== null) {
        params.push(`offset=${offset}`);
    }

    url += params.join("&");

    return await fetch(url)
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Marks the given alert history as read
export async function mark_alert_read({
    alert_history_id
}) {

    if (alert_history_id == null) {
        return null;
    }

    const url =
        config.api_url +
        `/api/v1/alerts/history/${alert_history_id}/mark/read`;

    return await fetch(url, {
        method: "POST"
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}

//Marks the given alert history as unread
export async function mark_alert_unread({
    alert_history_id
}) {

    if (alert_history_id == null) {
        return null;
    }

    const url =
        config.api_url +
        `/api/v1/alerts/history/${alert_history_id}/mark/unread`;

    return await fetch(url, {
        method: "POST"
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}

//ALERT RULES
//Returns all alert rules
export async function get_all_alert_rules() {

    const url =
        config.api_url +
        "/api/v1/alerts/rule/all";

    return await fetch(url)
        .then(res => res.json())
        .catch(err => console.error(err));
}

//Adds a new custom alert rule. Does NOT support nesting currently.
export async function add_alert_rule({
    name,
    description = null,
    params
}) {

    if (name == null || params == null) {
        return null;
    }

    const body = {
        name,
        params
    };

    if (description !== null) {
        body.description = description;
    }

    const url =
        config.api_url +
        "/api/v1/alerts/rule/add";

    return await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}

//Updates an existing alert rule. Supports partial updates.
export async function update_alert_rule({
    alert_rule_id,
    name = null,
    description = null,
    params = null
}) {

    if (alert_rule_id == null) {
        return null;
    }

    if (
        name == null &&
        description == null &&
        params == null
    ) {
        return null;
    }

    const body = {};

    if (name !== null) {
        body.name = name;
    }

    if (description !== null) {
        body.description = description;
    }

    if (params !== null) {
        body.params = params;
    }

    const url =
        config.api_url +
        `/api/v1/alerts/rule/${alert_rule_id}/update`;

    return await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}

//Marks the given alert rule as disabled
export async function disable_alert_rule({
    alert_rule_id
}) {

    if (alert_rule_id == null) {
        return null;
    }

    const url =
        config.api_url +
        `/api/v1/alerts/rule/${alert_rule_id}/mark/disable`;

    return await fetch(url, {
        method: "POST"
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}

//Marks the given alert rule as enabled
export async function enable_alert_rule({
    alert_rule_id
}) {

    if (alert_rule_id == null) {
        return null;
    }

    const url =
        config.api_url +
        `/api/v1/alerts/rule/${alert_rule_id}/mark/enable`;

    return await fetch(url, {
        method: "POST"
    })
    .then(res => res.json())
    .catch(err => console.error(err));
}