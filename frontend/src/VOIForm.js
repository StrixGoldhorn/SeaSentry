import { useState, useEffect } from "react";
import { add_VOI } from "./utils";
import { update_VOI } from "./utils";
import { useSnackbar } from "./SnackbarContext";

export default function VOIPanel({
    initialVOI = null,
    onSaved = null,
}){

    const emptyForm = {
        name: "",
        desc: "",
        mmsi: "",
        imo: "",
    };

    const [form, setForm] = useState(
        initialVOI
            ? {
                name: initialVOI.vessel_of_interest_desc_name,
                desc: initialVOI.vessel_of_interest_description ?? "",
                mmsi: initialVOI.vessel_of_interest_mmsi ?? "",
                imo: initialVOI.vessel_of_interest_imo ?? "",
            }
            : emptyForm
    );

    const [response,setResponse]=useState("");
    const { showSnackbar } = useSnackbar();

    const submit = async () => {
        try {
            let data;

            if (initialVOI) {
                data = await update_VOI({
                    voi_id: initialVOI.vessel_of_interest_id,
                    name: form.name,
                    desc: form.desc || null,
                    mmsi: form.mmsi || null,
                    imo: form.imo || null,
                });
            } else {
                data = await add_VOI({
                    name: form.name,
                    desc: form.desc || null,
                    mmsi: form.mmsi || null,
                    imo: form.imo || null,
                });
            }
            
            setResponse(JSON.stringify(data, null, 2));

            if (data?.error) {
                showSnackbar(`Error saving VOI: ${data.error}`);
                return;
            } else if (data?.status && data.status >= 400) {
                showSnackbar(`Error saving VOI: Status ${data.status}`);
                return;
            }

            showSnackbar("VOI saved successfully", "success");
            onSaved?.();
            if (!initialVOI) {
                setForm(emptyForm);
            }
        } catch (err) {
            console.error(err);
            setResponse(String(err));
            showSnackbar(`Error saving VOI: ${err}`);
        }
    };

    useEffect(() => {
        if (!initialVOI) {
            setForm(emptyForm);
            return;
        }

        setForm({
            name: initialVOI.vessel_of_interest_desc_name,
            desc: initialVOI.vessel_of_interest_description ?? "",
            mmsi: initialVOI.vessel_of_interest_mmsi ?? "",
            imo: initialVOI.vessel_of_interest_imo ?? "",
        });
    }, [initialVOI]);

    return(

        <div className="coord-grid">
        <div className="form-group">

            <h2>
                {initialVOI
                    ? "Edit Vessel Of Interest"
                    : "Add Vessel Of Interest"}
            </h2>

            <input placeholder="Name"
            value={form.name}
            onChange={e=>setForm({...form,name:e.target.value})}
            />

            <input placeholder="Description"
            value={form.desc}
            onChange={e=>setForm({...form,desc:e.target.value})}
            />

            <input placeholder="MMSI"
            value={form.mmsi}
            onChange={e=>setForm({...form,mmsi:e.target.value})}
            />

            <input placeholder="IMO"
            value={form.imo}
            onChange={e=>setForm({...form,imo:e.target.value})}
            />

            <button onClick={submit}>
                {initialVOI
                    ? "Edit VOI"
                    : "Add VOI"}
            </button>

            {initialVOI && (
                <button
                    onClick={() => {
                        setForm(emptyForm);
                        onSaved?.();
                    }}
                >
                    Cancel
                </button>
            )}

            <pre>{response}</pre>

        </div>
        </div>

    );

}