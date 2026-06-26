import { useState } from "react";
import { add_box_AOI } from "./utils";

export default function AOIPanel(){

    const [form,setForm]=useState({

        lat_min:"",
        lat_max:"",
        long_min:"",
        long_max:"",
        name:"",
        desc:"",
        
    });

    const [response,setResponse]=useState("");

    const submit=async()=>{

        const data = await add_box_AOI({

            lat_min:Number(form.lat_min),

            lat_max:Number(form.lat_max),

            long_min:Number(form.long_min),

            long_max:Number(form.long_max),

            name:form.name,

            desc:form.desc||null,

        });

        setResponse(JSON.stringify(data,null,2));

    };

    return(

        <div>

            <h2>Add AOI Box</h2>

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
                Add AOI
            </button>

            <pre>{response}</pre>

        </div>

    );

}