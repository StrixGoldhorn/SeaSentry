import { useState } from "react";
import { add_box_geofence } from "./utils";

export default function GeofencePanel(){

    const [form,setForm]=useState({
        name:"",
        desc:"",
        lat_min:"",
        lat_max:"",
        long_min:"",
        long_max:""
    });

    const [response,setResponse]=useState("");

    async function submit(){

        const data=await add_box_geofence({

            name:form.name,

            desc:form.desc||null,

            lat_min:Number(form.lat_min),

            lat_max:Number(form.lat_max),

            long_min:Number(form.long_min),

            long_max:Number(form.long_max)

        });

        setResponse(JSON.stringify(data,null,2));

    }

    return(
        <div className="coord-grid">
        <div className="form-group">
            <h2>Add Geofence Box</h2>

            <input placeholder="Name"
                onChange={e=>setForm({...form,name:e.target.value})}
            />

            <input placeholder="Description"
                onChange={e=>setForm({...form,desc:e.target.value})}
            />

            <input placeholder="Lat Min"
                onChange={e=>setForm({...form,lat_min:e.target.value})}
            />

            <input placeholder="Lat Max"
                onChange={e=>setForm({...form,lat_max:e.target.value})}
            />

            <input placeholder="Long Min"
                onChange={e=>setForm({...form,long_min:e.target.value})}
            />

            <input placeholder="Long Max"
                onChange={e=>setForm({...form,long_max:e.target.value})}
            />

            <button onClick={submit}>
                Add Geofence
            </button>

            <pre>{response}</pre>

        </div>
        </div>
    );

}