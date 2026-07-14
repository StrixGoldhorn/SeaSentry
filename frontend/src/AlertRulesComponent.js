import { useState } from "react";
import AlertRulesList from "./AlertRulesDisplay";
import AlertRuleForm from "./AlertRuleForm";

export default function AlertRulesComponent() {
    const [editingRule, setEditingRule] = useState(null);
    const [refreshKey, setRefreshKey] = useState(0);

    return (
        <>
            <AlertRuleForm
                initialRule={editingRule}
                onSaved={() => {
                    setEditingRule(null);
                    setRefreshKey(k => k + 1);
                }}
            />

            <AlertRulesList
                onEdit={setEditingRule}            
                refreshKey={refreshKey}
            />
        </>
    );
}