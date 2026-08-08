import { useEffect, useState } from "react";
import {
    get_all_alert_rules,
    enable_alert_rule,
    disable_alert_rule,
    delete_alert_rule
} from "./utils";

export default function AlertRulesList({
    onEdit,
    refreshKey
}) {

    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadRules = async () => {
        setLoading(true);

        try {
            const data = await get_all_alert_rules();
            if (data?.error) {
                alert(`Error loading alert rules: ${data.error}`);
            } else if (data?.status && data.status >= 400) {
                alert(`Error loading alert rules: Status ${data.status}`);
            }
            if (data?.data) {
                setRules(data.data);
            } else if (Array.isArray(data)) {
                setRules(data);
            }
        } catch (err) {
            console.error(err);
            alert(`Error loading alert rules: ${err}`);
        }

        setLoading(false);
    };

    useEffect(() => {
        loadRules();
    }, [refreshKey]);

    const toggleRule = async (rule) => {
        try {
            let res;
            if (rule.alert_rule_enabled) {
                res = await disable_alert_rule({
                    alert_rule_id: rule.alert_rule_id
                });
            } else {
                res = await enable_alert_rule({
                    alert_rule_id: rule.alert_rule_id
                });
            }
            if (res?.error) {
                alert(`Error toggling rule: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                alert(`Error toggling rule: Status ${res.status}`);
            } else {
                await loadRules();
            }
        } catch (err) {
            console.error(err);
            alert(`Error toggling rule: ${err}`);
        }
    };

    async function handleDelete(rule) {

        const confirmed = window.confirm(
            `Delete "${rule.alert_rule_name}"?`
        );

        if (!confirmed) return;

        try {
            const res = await delete_alert_rule({
                alert_rule_id: rule.alert_rule_id,
                alert_rule_name: rule.alert_rule_name
            });
            if (res?.error) {
                alert(`Error deleting rule: ${res.error}`);
            } else if (res?.status && res.status >= 400) {
                alert(`Error deleting rule: Status ${res.status}`);
            } else {
                await loadRules();
            }
        } catch (err) {
            console.error(err);
            alert(`Error deleting rule: ${err}`);
        }
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

                        <details style={{ marginTop: "10px" }}>
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