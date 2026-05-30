export async function get_ships_past_day({lat_min, lat_max, long_min, long_max, limit = null, time_within = null}) {
    if (lat_min == null || lat_max == null || long_min == null || long_max == null) {
        return null;
    }


    var url = `http://localhost:5000/api/v1/vessels/bbox?`
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