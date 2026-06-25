import { useState } from "react";
import { add_alert_rule } from "./utils";

export default function AlertRulePanel() {

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

    const submit = async () => {

        const params = {

            field: form.field,
            operator: form.operator,
            value:
                form.value === ""
                    ? null
                    : isNaN(form.value)
                    ? form.value
                    : Number(form.value)

        };

        if (form.valueGeofenceid !== "") {
            params.valueGeofenceid = Number(form.valueGeofenceid);
        }

        if (form.valueShiptype !== "") {
            params.valueShiptype = form.valueShiptype;
        }

        const data = await add_alert_rule({

            name: form.name,

            description:
                form.description || null,

            params

        });

        setResponse(
            JSON.stringify(data, null, 2)
        );
    };

    const needsGeofence =
        form.field === "inside_geofence" ||
        form.field === "enter_geofence" ||
        form.field === "exit_geofence";

    const needsShiptype =
        form.field === "proximity_to_shiptype";

    return (

        <div>

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

            <label>Field</label>

            <select
                value={form.field}
                onChange={e =>
                    setForm({
                        ...form,
                        field: e.target.value
                    })
                }
            >

                <option value="shipname">
                    shipname
                </option>

                <option value="shiptype">
                    shiptype
                </option>

                <option value="mmsi">
                    mmsi
                </option>

                <option value="speed">
                    speed
                </option>

                <option value="proximity_to_shiptype">
                    proximity_to_shiptype
                </option>

                <option value="inside_geofence">
                    inside_geofence
                </option>

                <option value="enter_geofence">
                    enter_geofence
                </option>

                <option value="exit_geofence">
                    exit_geofence
                </option>

                <option value="is_vessel_of_interest">
                    is_vessel_of_interest
                </option>

            </select>

            <br />

            <label>Operator</label>

            <select
                value={form.operator}
                onChange={e =>
                    setForm({
                        ...form,
                        operator: e.target.value
                    })
                }
            >

                <option value="=">=</option>

                <option value="!=">!=</option>

                <option value=">">{">"}</option>

                <option value="<">{"<"}</option>

                <option value=">=">{">="}</option>

                <option value="<=">{"<="}</option>

                <option value="LIKE">
                    LIKE
                </option>

            </select>

            <br />

            <input
                placeholder="Value"
                value={form.value}
                onChange={e =>
                    setForm({
                        ...form,
                        value: e.target.value
                    })
                }
            />

            {needsGeofence && (

                <input
                    placeholder="Geofence ID"
                    value={form.valueGeofenceid}
                    onChange={e =>
                        setForm({
                            ...form,
                            valueGeofenceid:
                                e.target.value
                        })
                    }
                />

            )}

            {needsShiptype && (

                <input
                    placeholder="Ship Type"
                    value={form.valueShiptype}
                    onChange={e =>
                        setForm({
                            ...form,
                            valueShiptype:
                                e.target.value
                        })
                    }
                />

            )}

            <br />

            <button onClick={submit}>
                Add Alert Rule
            </button>

            <pre>{response}</pre>

        </div>

    );
}