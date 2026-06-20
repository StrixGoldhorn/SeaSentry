import { useState } from "react"
import { get_ships_past_day } from "./utils"

//

//DEPRECATED, DO NOT USE

//
export function AOIadd ({ getAOIcoords }) {

    const [latmin, setlatmin] = useState("");
    const [latmax, setlatmax] = useState("");
    const [longmin, setlongmin] = useState("");
    const [longmax, setlongmax] = useState("");

    function passCoordsUp() {
        // if (latmin.trim() === "" || latmax.trim() === "" || longmin.trim() === "" || longmax.trim() === "") return;

        getAOIcoords({"lat_min": Number(latmin), 
            "lat_max": Number(latmax), 
            "long_min": Number(longmin), 
            "long_max": Number(longmax)});
        
        setlatmin("");
        setlatmax("");
        setlongmin("");
        setlongmax("");
    }





    return (
        <div id="aoiadd">
                <input type="number" id="latmin" placeholder="latmin" value={latmin} onChange={(e) => setlatmin(e.target.value)}></input>
                <input type="number" id="latmax" placeholder="latmax" value={latmax} onChange={(e) => setlatmax(e.target.value)}></input>
                <input type="number" id="longmin" placeholder="longmin" value={longmin} onChange={(e) => setlongmin(e.target.value)}></input>
                <input type="number" id="longmax" placeholder="longmax" value={longmax} onChange={(e) => setlongmax(e.target.value)}></input>
                <button id="aoiaddbutton" type="button" onClick={passCoordsUp}>Add</button>
        </div>
    )
}