import { useEffect, useState } from "react";
import {
    get_all_alert_rules,
    enable_alert_rule,
    disable_alert_rule,
    delete_alert_rule
} from "./utils";
import './css/Alerts.css';

export default function AlertRulesList({
    onEdit,
    refreshKey
}) {

    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadRules = async () => {
        setLoading(true);

        const data = await get_all_alert_rules();

        if (data?.data) {
            setRules(data.data);
        } else if (Array.isArray(data)) {
            setRules(data);
        }

        setLoading(false);
    };

    useEffect(() => {
        loadRules();
    }, [refreshKey]);

    const toggleRule = async (rule) => {

        if (rule.alert_rule_enabled) {

            await disable_alert_rule({
                alert_rule_id: rule.alert_rule_id
            });

        } else {

            await enable_alert_rule({
                alert_rule_id: rule.alert_rule_id
            });

        }

        await loadRules();
    };

    async function handleDelete(rule) {

        const confirmed = window.confirm(
            `Delete "${rule.alert_rule_name}"?`
        );

        if (!confirmed) return;

        await delete_alert_rule({
            alert_rule_id: rule.alert_rule_id,
            alert_rule_name: rule.alert_rule_name
        });

        await loadRules();
    }

    if (loading) {
        return <div>Loading alert rules...</div>;
    }

    return (
        <div className="alert-rule">

            <h2>Alert Rules</h2>

            {rules.length === 0 && (
                <div>No alert rules found.</div>
            )}

            {rules.map(rule => {

                const id = rule.alert_rule_id;

                const name = rule.alert_rule_name;

                const description = rule.alert_rule_description;

                const enabled = rule.alert_rule_enabled;

                const params = rule.alert_rule_params;

                return (

                    <div
                        key={id}
                        style={{
                            border: "1px solid gray",
                            padding: "12px",
                            marginBottom: "12px",
                            borderRadius: "8px"
                        }}
                    >

                        <h3>{name}</h3>

                        <p>
                            {description || "No description"}
                        </p>

                        <p>
                            <strong>Status:</strong>{" "}
                            {enabled ? "Enabled" : "Disabled"}
                        </p>

                        <button
                            onClick={() => toggleRule(rule)}
                        >
                            {enabled ? "Disable" : "Enable"}
                        </button>

                        <button
                            onClick={() => onEdit(rule)}
                        >
                            Edit
                        </button>

                        <button
                            onClick={() => handleDelete(rule)}
                            style={{
                                background: "#cc3333",
                                color: "white",
                                border: "none",
                                padding: "6px 12px",
                                cursor: "pointer"
                            }}
                        >
                            Delete
                        </button>

                        <details>
                            <summary>Show Rule JSON</summary>

                            <pre>
                                {JSON.stringify(params, null, 2)}
                            </pre>
                        </details>

                    </div>

                );

            })}
        </div>
    );
}