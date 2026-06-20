//VESSELS
//Query latest vessel positions within a bounding box
export async function get_ships_on_screen({lat_min, lat_max, long_min, long_max, limit = null, time_within = null}) {
    if (lat_min == null || lat_max == null || long_min == null || long_max == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/vessels/bbox?`
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


    let url = `http://localhost:5000/api/v1/vessels/`
    +`${vessel_data_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Updates an existing Vessel. Supports partial updates.
export async function update_ship_using_data_id({vessel_data_id, ship_name = null, ship_type = null, flag = null, 
    length_meters = null, beam_meters = null, user_tags = null}) {
    if (ship_name == null && ship_type == null && flag == null && length_meters == null && beam_meters == null && user_tags == null) {
        return null;
    }

    if (vessel_data_id == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/vessels/`
    +`${vessel_data_id}/update?`;

    if (ship_name !== null) {
        url = url + `ship_name=${ship_name}&`;
    }

    if (ship_type !== null) {
        url = url + `ship_type=${ship_type}&`;
    }

    if (flag !== null) {
        url = url + `flag=${flag}&`;
    }

    if (length_meters !== null) {
        url = url + `length_meters=${length_meters}&`;
    }

    if (beam_meters !== null) {
        url = url + `beam_meters=${beam_meters}&`;
    }

    if (user_tags !== null) {
        url = url + `user_tags=${user_tags}&`;
    }
    

    return await fetch(url, {method: "PATCH"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//VESSELS OF INTEREST
//Query for all vessels of interest
export async function get_all_VOI() {

    let url = `http://localhost:5000/api/v1/vessel_of_interest/get/all`
    
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


    let url = `http://localhost:5000/api/v1/vessel_of_interest/`
    +`${voi_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified vessel of interest
export async function add_VOI({name, desc = null, mmsi, imo}) {

    if (name == null) {
        return null;
    }
    if (mmsi == null && imo == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/vessel_of_interest/add?`
    +`name=${name}&`;

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }

    if (mmsi !== null) {
        url = url + `mmsi=${mmsi}&`;
    }

    if (imo !== null) {
        url = url + `imo=${imo}&`;
    }

    return await fetch(url, {method: "POST"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//AOI
//Query for all AOIs
export async function get_all_AOI() {

    let url = `http://localhost:5000/api/v1/aois/get/all`
    
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


    let url = `http://localhost:5000/api/v1/aois/`
    +`${aoi_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified bounding box.
export async function add_box_AOI({lat_min, lat_max, long_min, long_max, name, desc = null}) {

    if (lat_min == null || lat_max == null || long_min == null || long_max == null || name == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/aois/add/box?`
    +`lat_min=${lat_min}&lat_max=${lat_max}&`
    +`long_min=${long_min}&long_max=${long_max}`
    +`name=${name}&`;

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }


    return await fetch(url, {method: "POST"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified bounding polygon.
export async function add_poly_AOI({coords, name, desc = null}) {

    if (coords == null || name == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/aois/add/polygon?`
    +`coords=${coords}&`
    +`name=${name}&`;

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }


    return await fetch(url, {method: "POST"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Updates an existing Area of Interest. Supports partial updates.
export async function update_AOI({aoi_id, name = null, desc = null, coords = null, lat_min = null, lat_max = null, long_min = null, long_max = null}) {

    if (aoi_id == null) {
        return null;
    }

    if (name == null && desc == null && coords == null && lat_min == null && lat_max == null && long_min == null && long_max == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/aois/${aoi_id}/update?`;

    if (name !== null) {
        url = url + `name=${name}&`;
    }

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }

    if (coords !== null) {
        url = url + `coords=${coords}&`;
    }

    if (lat_min !== null) {
        url = url + `lat_min=${lat_min}&`;
    }

    if (lat_max !== null) {
        url = url + `lat_max=${lat_max}&`;
    }

    if (long_min !== null) {
        url = url + `long_min=${long_min}&`;
    }

    if (long_max !== null) {
        url = url + `long_max=${long_max}&`;
    }

    return await fetch(url, {method: "PATCH"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//GEOFENCES
//Query for all Geofences
export async function get_all_geofences() {

    let url = `http://localhost:5000/api/v1/geofences/get/all`
    
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


    let url = `http://localhost:5000/api/v1/geofences/`
    +`${geofence_id}`;

    return await fetch(url)
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified bounding box.
export async function add_box_geofence({lat_min, lat_max, long_min, long_max, name, desc = null}) {

    if (lat_min == null || lat_max == null || long_min == null || long_max == null || name == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/geofences/add/box?`
    +`lat_min=${lat_min}&lat_max=${lat_max}&`
    +`long_min=${long_min}&long_max=${long_max}`
    +`name=${name}&`;

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }


    return await fetch(url, {method: "POST"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Adds specified bounding polygon.
export async function add_poly_geofence({coords, name, desc = null}) {

    if (coords == null || name == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/geofences/add/polygon?`
    +`coords=${coords}&`
    +`name=${name}&`;

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }


    return await fetch(url, {method: "POST"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}

//Updates an existing geofence. Supports partial updates.
export async function update_geofence({geofence_id, name = null, desc = null, coords = null, lat_min = null, lat_max = null, long_min = null, long_max = null}) {

    if (geofence_id == null) {
        return null;
    }

    if (name == null && desc == null && coords == null && lat_min == null && lat_max == null && long_min == null && long_max == null) {
        return null;
    }


    let url = `http://localhost:5000/api/v1/geofences/${geofence_id}/update?`;

    if (name !== null) {
        url = url + `name=${name}&`;
    }

    if (desc !== null) {
        url = url + `desc=${desc}&`;
    }

    if (coords !== null) {
        url = url + `coords=${coords}&`;
    }

    if (lat_min !== null) {
        url = url + `lat_min=${lat_min}&`;
    }

    if (lat_max !== null) {
        url = url + `lat_max=${lat_max}&`;
    }

    if (long_min !== null) {
        url = url + `long_min=${long_min}&`;
    }

    if (long_max !== null) {
        url = url + `long_max=${long_max}&`;
    }

    return await fetch(url, {method: "PATCH"})
    .then(res => res.json())
    .then(data => data)
    .catch(err => console.error(err));
}
