//DEPRECATED CODE, DO NOT USE

// export async function update_ship_using_data_id({vessel_data_id, ship_name = null, ship_type = null, flag = null, 
//     length_meters = null, beam_meters = null, user_tags = null}) {
//     if (ship_name == null && ship_type == null && flag == null && length_meters == null && beam_meters == null && user_tags == null) {
//         return null;
//     }

//     if (vessel_data_id == null) {
//         return null;
//     }


//     let url = config.api_url + `/api/v1/vessels/`
//     +`${vessel_data_id}/update?`;

//     if (ship_name !== null) {
//         url = url + `ship_name=${ship_name}&`;
//     }

//     if (ship_type !== null) {
//         url = url + `ship_type=${ship_type}&`;
//     }

//     if (flag !== null) {
//         url = url + `flag=${flag}&`;
//     }

//     if (length_meters !== null) {
//         url = url + `length_meters=${length_meters}&`;
//     }

//     if (beam_meters !== null) {
//         url = url + `beam_meters=${beam_meters}&`;
//     }

//     if (user_tags !== null) {
//         url = url + `user_tags=${user_tags}&`;
//     }
    

//     return await fetch(url, {method: "PATCH"})
//     .then(res => res.json())
//     .then(data => data)
//     .catch(err => console.error(err));
// }

// export async function add_VOI({name, desc = null, mmsi, imo}) {

//     if (name == null) {
//         return null;
//     }
//     if (mmsi == null && imo == null) {
//         return null;
//     }


//     let url = config.api_url + `/api/v1/vessel_of_interest/add?`
//     +`name=${name}&`;

//     if (desc !== null) {
//         url = url + `desc=${desc}&`;
//     }

//     if (mmsi !== null) {
//         url = url + `mmsi=${mmsi}&`;
//     }

//     if (imo !== null) {
//         url = url + `imo=${imo}&`;
//     }

//     return await fetch(url, {method: "POST"})
//     .then(res => res.json())
//     .then(data => data)
//     .catch(err => console.error(err));
// }

// export async function add_box_AOI({lat_min, lat_max, long_min, long_max, name, desc = null}) {

//     if (lat_min == null || lat_max == null || long_min == null || long_max == null || name == null) {
//         return null;
//     }


//     let url = config.api_url + `/api/v1/aois/add/box?`
//     +`lat_min=${lat_min}&lat_max=${lat_max}&`
//     +`long_min=${long_min}&long_max=${long_max}&`
//     +`name=${encodeURIComponent(name)}&`;

//     if (desc !== null) {
//         url = url + `desc=${encodeURIComponent(desc)}&`;
//     }

// console.log(url);
//     return await fetch(url, {method: "POST"})
//     .then(res => res.json())
//     .then(data => data)
//     .catch(err => console.error(err));
// }