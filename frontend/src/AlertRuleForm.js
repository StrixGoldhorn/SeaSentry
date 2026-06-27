import { useEffect, useState } from "react";
import {
    add_alert_rule,
    get_all_geofences
} from "./utils";


const FIELD_CONFIG = {

    shipname: {
        operators: ["=", "LIKE"],
        needsValue: true
    },

    shiptype: {
        operators: ["=", "!="],
        needsValue: true
    },

    mmsi: {
        operators: ["="],
        needsValue: true
    },

    speed: {
        operators: ["=", ">", "<", ">=", "<="],
        needsValue: true
    },

    proximity_to_shiptype: {
        operators: ["="],
        needsValue: true,
        needsShiptype: true
    },

    inside_geofence: {
        operators: ["="],
        needsGeofence: true
    },

    enter_geofence: {
        operators: ["="],
        needsGeofence: true
    },

    exit_geofence: {
        operators: ["="],
        needsGeofence: true
    },

    is_vessel_of_interest: {
        operators: ["="]
    }

};

const SHIP_TYPES = [
    "Cargo",
    "Tanker",
    "Tug",
    "Passenger",
    "Fishing",
    "Pleasure Craft",
    "Military",
    "Other"
];

export default function AlertRulePanel() {

    const [geofences, setGeofences] = useState([]);

    const [form, setForm] = useState({

        name: "",
        description: "",

        field: "speed",
        operator: ">",

        value: "",

        valueGeofenceid: "",
        valueShiptype: ""

    });

    const [response, setResponse] = useState("");

    useEffect(() => {

        get_all_geofences()
            .then(data => {

                if (data?.data) {
                    setGeofences(data.data);
                }

            });

    }, []);

    const fieldConfig =
        FIELD_CONFIG[form.field];

    const submit = async () => {

        const params = {

            field: form.field,

            operator: form.operator

        };

        if (
            form.field === "inside_geofence" ||
            form.field === "enter_geofence" ||
            form.field === "exit_geofence" ||
            form.field === "is_vessel_of_interest"
        ) {

            params.value = true;

        } else if (form.field === "speed") {

            params.value = Number(form.value);

        } else {

            params.value = form.value;

        }

        if (fieldConfig.needsGeofence) {

            params.valueGeofenceid =
                Number(form.valueGeofenceid);

        }

        if (fieldConfig.needsShiptype) {

            params.valueShiptype =
                form.valueShiptype;

        }

        const data =
            await add_alert_rule({

                name: form.name,

                description:
                    form.description || null,

                params

            });

        setResponse(
            JSON.stringify(data, null, 2)
        );
    };

    return (

        <div className="coord-grid">
        <div className="form-group">

            <h2>Add Alert Rule</h2>

            <input
                placeholder="Rule Name"
                value={form.name}
                onChange={e =>
                    setForm({
                        ...form,
                        name: e.target.value
                    })
                }
            />

            <br />

            <input
                placeholder="Description"
                value={form.description}
                onChange={e =>
                    setForm({
                        ...form,
                        description: e.target.value
                    })
                }
            />

            <br />
            <br />

            <label>Field</label>

            <br />

            <select
                value={form.field}
                onChange={e => {

                    const newField =
                        e.target.value;

                    setForm({

                        ...form,

                        field: newField,

                        operator:
                            FIELD_CONFIG[
                                newField
                            ].operators[0]

                    });

                }}
            >

                {Object.keys(FIELD_CONFIG)
                    .map(field => (

                        <option
                            key={field}
                            value={field}
                        >
                            {field}
                        </option>

                    ))}

            </select>

            <br />
            <br />

            <label>Operator</label>

            <br />

            <select
                value={form.operator}
                onChange={e =>
                    setForm({
                        ...form,
                        operator: e.target.value
                    })
                }
            >

                {fieldConfig.operators.map(op => (

                    <option
                        key={op}
                        value={op}
                    >
                        {op}
                    </option>

                ))}

            </select>

            <br />
            <br />

            {fieldConfig.needsValue && (

                <>
                    <label>Value</label>

                    <br />

                    <input
                        value={form.value}
                        placeholder="Value"
                        onChange={e =>
                            setForm({
                                ...form,
                                value: e.target.value
                            })
                        }
                    />

                    <br />
                    <br />
                </>

            )}

            {fieldConfig.needsShiptype && (

                <>

                    <label>Ship Type</label>

                    <br />

                    <select
                        value={form.valueShiptype}
                        onChange={e =>
                            setForm({
                                ...form,
                                valueShiptype:
                                    e.target.value
                            })
                        }
                    >

                        <option value="">
                            Select Ship Type
                        </option>

                        {SHIP_TYPES.map(type => (

                            <option
                                key={type}
                                value={type}
                            >
                                {type}
                            </option>

                        ))}

                    </select>

                    <br />
                    <br />

                </>

            )}

            {fieldConfig.needsGeofence && (

                <>

                    <label>Geofence</label>

                    <br />

                    <select
                        value={
                            form.valueGeofenceid
                        }
                        onChange={e =>
                            setForm({
                                ...form,
                                valueGeofenceid:
                                    e.target.value
                            })
                        }
                    >

                        <option value="">
                            Select Geofence
                        </option>

                        {geofences.map(
                            geofence => (

                                <option
                                    key={
                                        geofence.geofence_id
                                    }
                                    value={
                                        geofence.geofence_id
                                    }
                                >

                                    {
                                        geofence.geofence_name
                                    }

                                </option>

                            )
                        )}

                    </select>

                    <br />
                    <br />

                </>

            )}

            <button onClick={submit}>
                Add Alert Rule
            </button>

            <pre>{response}</pre>

        </div>
        </div>

    );
}