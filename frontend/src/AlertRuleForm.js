import { useEffect, useMemo, useState } from "react";
import { QueryBuilder } from "react-querybuilder";
import "react-querybuilder/dist/query-builder.css";

import {
  add_alert_rule,
  update_alert_rule,
  get_all_geofences,
} from "./utils";

export const fields = [
  { name: "shipname", label: "Ship Name" },
  { name: "shiptype", label: "Ship Type" },
  { name: "mmsi", label: "MMSI" },
  { name: "speed", label: "Speed" },
  { name: "proximity_to_shipname", label: "Proximity To Ship Name" },
  { name: "proximity_to_shiptype", label: "Proximity To Ship Type" },
  { name: "proximity_to_mmsi", label: "Proximity To MMSI" },
  { name: "inside_geofence", label: "Inside Geofence" },
  { name: "enter_geofence", label: "Enter Geofence" },
  { name: "exit_geofence", label: "Exit Geofence" },
  { name: "is_vessel_of_interest", label: "Is Vessel Of Interest" },
  { name: "has_usertag", label: "Has User Tag" },
];

const combinators = [
  { name: "and", label: "AND" },
  { name: "or", label: "OR" },
  { name: "not", label: "NOT" },
];

const operatorMap = {
  shipname: [
    { name: "=", label: "=" },
    { name: "LIKE", label: "LIKE" },
  ],

  shiptype: [
    { name: "=", label: "=" },
    { name: "!=", label: "!=" },
  ],

  mmsi: [
    { name: "=", label: "=" },
  ],

  speed: [
    { name: "=", label: "=" },
    { name: ">", label: ">" },
    { name: "<", label: "<" },
    { name: ">=", label: ">=" },
    { name: "<=", label: "<=" },
  ],

  proximity_to_shipname: [
    { name: "=", label: "=" },
  ],

  proximity_to_shiptype: [
    { name: "=", label: "=" },
  ],

  proximity_to_mmsi: [
    { name: "=", label: "=" },
  ],

  inside_geofence: [
    { name: "=", label: "=" },
  ],

  enter_geofence: [
    { name: "=", label: "=" },
  ],

  exit_geofence: [
    { name: "=", label: "=" },
  ],

  is_vessel_of_interest: [
    { name: "=", label: "=" },
  ],
};

export function OperatorSelector(props) {
  const operators =
    operatorMap[props.field] ??
    [{ name: "=", label: "=" }];

  return (
    <select
      value={props.value}
      onChange={(e) => props.handleOnChange(e.target.value)}
    >
      {operators.map((op) => (
        <option
          key={op.name}
          value={op.name}
        >
          {op.label}
        </option>
      ))}
    </select>
  );
}

export function CustomValueEditor(props) {
  const {
    field,
    value,
    handleOnChange,
    context,
  } = props;

  const geofences = context.geofences;

  if (
    field === "inside_geofence" ||
    field === "enter_geofence" ||
    field === "exit_geofence"
  ) {
    let current = {};

    try {
      current =
        typeof value === "string"
          ? JSON.parse(value || "{}")
          : value || {};
    } catch {
      current = {};
    }

    return (
      <select
        value={current.geofenceId ?? ""}
        onChange={(e) =>
          handleOnChange(
            JSON.stringify({
              geofenceId: Number(e.target.value),
            })
          )
        }
      >
        <option value="">
          Select Geofence
        </option>

        {geofences.map((g) => (
          <option
            key={g.geofence_id}
            value={g.geofence_id}
          >
            {g.geofence_name}
          </option>
        ))}
      </select>
    );
  }

  if (field === "proximity_to_shiptype" ||
      field === "proximity_to_shipname" ||
      field === "proximity_to_mmsi") {
    let current = {};

    try {
      current =
        typeof value === "string"
          ? JSON.parse(value || "{}")
          : value || {};
    } catch {
      current = {};
    }

    return (
      <>
        <input
          type="number"
          placeholder="Distance (m)"
          value={current.distance ?? ""}
          onChange={(e) =>
            handleOnChange(
              JSON.stringify({
                ...current,
                distance: Number(e.target.value),
              })
            )
          }
        />
        {field === "proximity_to_shiptype" && (
          <input
            type="text"
            placeholder="Ship Type"
            value={current.shiptype ?? ""}
            onChange={(e) =>
              handleOnChange(
                JSON.stringify({
                  ...current,
                  shiptype: e.target.value,
                })
              )
            }
          />
        )}

        {field === "proximity_to_shipname" && (
          <input
            type="text"
            placeholder="Ship Name"
            value={current.shipname ?? ""}
            onChange={(e) =>
              handleOnChange(
                JSON.stringify({
                  ...current,
                  shipname: e.target.value,
                })
              )
            }
          />
        )}

        {field === "proximity_to_mmsi" && (
          <input
            type="text"
            placeholder="MMSI"
            value={current.mmsi ?? ""}
            onChange={(e) =>
              handleOnChange(
                JSON.stringify({
                  ...current,
                  mmsi: e.target.value,
                })
              )
            }
          />
        )}
      </>
    );
  }

  if (field === "is_vessel_of_interest") {
    return (
      <input
        disabled
        value="true"
      />
    );
  }

  if (field === "speed") {
    return (
      <input
        type="number"
        value={value}
        onChange={(e) =>
          handleOnChange(e.target.value)
        }
      />
    );
  }

  return (
    <input
      value={value}
      onChange={(e) =>
        handleOnChange(e.target.value)
      }
    />
  );
}


export function convertRule(rule) {

  if ("rules" in rule) {
    
    const convertedRules = rule.rules.map(convertRule);

    if (
      rule.combinator !== "not" &&
      convertedRules.length === 1
    ) {
      return convertedRules[0];
    }

    return {
      combinator: rule.combinator,
      rules: convertedRules,
    };
  }

  const result = {
    field: rule.field,
    operator: rule.operator,
  };

  switch (rule.field) {
    case "speed":
      result.value = Number(rule.value);
      break;

    case "shipname":
    case "shiptype":
    case "mmsi":
      result.value = rule.value;
      break;

    case "inside_geofence":
    case "enter_geofence":
    case "exit_geofence": {
      const data =
        typeof rule.value === "string"
          ? JSON.parse(rule.value || "{}")
          : rule.value;

      result.value = true;
      result.valueGeofenceid =
        Number(data.geofenceId);

      break;
    }

    case "is_vessel_of_interest":
      result.value = true;
      break;

    case "proximity_to_shiptype":
    case "proximity_to_shipname":
    case "proximity_to_mmsi": {
      const data =
        typeof rule.value === "string"
          ? JSON.parse(rule.value || "{}")
          : rule.value;

      result.value = Number(data.distance);

      if (rule.field === "proximity_to_shiptype") {
        result.valueShiptype = data.shiptype;
      }

      if (rule.field === "proximity_to_shipname") {
        result.valueShipname = data.shipname;
      }

      if (rule.field === "proximity_to_mmsi") {
        result.valueShipmmsi = data.mmsi;
      }

      break;
    }


    default:
      result.value = rule.value;
  }

  return result;
}

function makeId() {
  return crypto.randomUUID();
}

export function parseRule(rule) {

  if (!rule.rules && rule.field) {

    const parsedRule = {
      id: makeId(),
      field: rule.field,
      operator: rule.operator,
    };

    switch (rule.field) {
      case "speed":
        parsedRule.value = String(rule.value);
        break;

      case "shipname":
      case "shiptype":
      case "mmsi":
        parsedRule.value = rule.value;
        break;

      case "inside_geofence":
      case "enter_geofence":
      case "exit_geofence":
        parsedRule.value = JSON.stringify({
          geofenceId: rule.valueGeofenceid,
        });
        break;

      case "is_vessel_of_interest":
        parsedRule.value = true;
        break;

      case "proximity_to_shiptype":
        parsedRule.value = JSON.stringify({
          distance: rule.value,
          shiptype: rule.valueShiptype,
        });
        break;

      case "proximity_to_shipname":
        parsedRule.value = JSON.stringify({
          distance: rule.value,
          shipname: rule.valueShipname,
        });
        break;

      case "proximity_to_mmsi":
        parsedRule.value = JSON.stringify({
          distance: rule.value,
          mmsi: rule.valueShipmmsi,
        });
        break;

      default:
        parsedRule.value = rule.value;
    }

    return {
      id: makeId(),
      combinator: "and",
      rules: [parsedRule],
    };
  }

  // Group
  if (rule.rules) {
    return {
      id: makeId(),
      combinator: rule.combinator,
      rules: rule.rules.map(parseRule),
    };
  }

  return rule;
}

export default function AlertRuleForm({
  initialRule = null,
  onSaved = null
}) {
  const [geofences, setGeofences] = useState([]);

  const [name, setName] = useState(initialRule?.alert_rule_name ?? "");
  const [description, setDescription] = useState(
      initialRule?.alert_rule_description ?? ""
  );

  const [query, setQuery] = useState(
      initialRule
          ? parseRule(initialRule.alert_rule_params)
          : {
              combinator: "and",
              rules: []
          }
  );

  const [response, setResponse] = useState("");

  useEffect(() => {
    async function loadGeofences() {
      try {
        const data = await get_all_geofences();

        if (data?.data) {
          setGeofences(data.data);
        }
      } catch (err) {
        console.error(err);
      }
    }

    loadGeofences();
  }, []);

  useEffect(() => {
    if (!initialRule) return;

    setName(initialRule.alert_rule_name);
    setDescription(initialRule.alert_rule_description ?? "");
    setQuery(parseRule(initialRule.alert_rule_params));
  }, [initialRule]);


  const context = useMemo(
    () => ({
      geofences,
    }),
    [geofences]
  );

  async function submit() {
    if (!name.trim()) {
      alert("Rule name is required.");
      return;
    }

    if (query.rules.length === 0) {
      alert("Please add at least one rule.");
      return;
    }

    try {
      const backendParams = convertRule(query);

      if (initialRule) {
          await update_alert_rule({
              alert_rule_id: initialRule.alert_rule_id,
              name,
              description,
              params: backendParams
          });
      } else {
          await add_alert_rule({
              name,
              description,
              params: backendParams
          });
      }

      onSaved?.();

      setName("");
      setDescription("");
      setQuery({
          combinator: "and",
          rules: [],
      });
      
    } catch (err) {
      console.error(err);
      setResponse(String(err));
    }
  }

  return (
    <div className="coord-grid">
      <div className="form-group">

        <h2>Add Alert Rule</h2>

        <input
          placeholder="Rule Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <br />
        <br />

        <input
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <br />
        <br />

        <QueryBuilder
          fields={fields}
          query={query}
          onQueryChange={setQuery}
          context={context}
          controlElements={{
            valueEditor: CustomValueEditor,
            operatorSelector: OperatorSelector,
          }}
          combinators={combinators}
          showCloneButtons
        />

        <br />

        <button onClick={submit}>
            {initialRule ? "Update Alert Rule" : "Add Alert Rule"}
        </button>

        {initialRule && (
          <button
            onClick={() => {
              setName("");
              setDescription("");
              setQuery({
                combinator: "and",
                rules: [],
              });

              onSaved?.();
            }}
          >
            Cancel
          </button>
        )}

        <br />
        <br />

        <h3>Backend JSON Preview</h3>

        <pre
          style={{
            maxHeight: 400,
            overflow: "auto",
            background: "#f5f5f5",
            padding: "1rem",
            borderRadius: 6,
          }}
        >
          {JSON.stringify(convertRule(query), null, 2)}
        </pre>

        <pre>{response}</pre>

      </div>
    </div>
  );
}