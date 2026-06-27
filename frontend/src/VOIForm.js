import { useState } from "react";
import { add_VOI } from "./utils";

export default function VOIPanel(){

    const [form,setForm]=useState({
        name:"",
        desc:"",
        mmsi:"",
        imo:""
    });

    const [response,setResponse]=useState("");

    const submit=async()=>{

        const data=await add_VOI({

            name:form.name,

            desc:form.desc||null,

            mmsi:form.mmsi||null,

            imo:form.imo||null

        });

        setResponse(JSON.stringify(data,null,2));

    };

    return(

        <div className="coord-grid">
        <div className="form-group">

            <h2>Add Vessel Of Interest</h2>

            <input placeholder="Name"
                onChange={e=>setForm({...form,name:e.target.value})}
            />

            <input placeholder="Description"
                onChange={e=>setForm({...form,desc:e.target.value})}
            />

            <input placeholder="MMSI"
                onChange={e=>setForm({...form,mmsi:e.target.value})}
            />

            <input placeholder="IMO"
                onChange={e=>setForm({...form,imo:e.target.value})}
            />

            <button onClick={submit}>
                Add VOI
            </button>

            <pre>{response}</pre>

        </div>
        </div>

    );

}