import { useState, useRef, useEffect } from "react";
import AlertRulesList from "./AlertRulesDisplay";
import AlertRuleForm from "./AlertRuleForm";

export default function AlertRulesComponent() {
    const [editingRule, setEditingRule] = useState(null);
    const [refreshKey, setRefreshKey] = useState(0);
    const formRef = useRef(null);
    const handleEdit = (rule) => {
        setEditingRule(rule);
    };

    useEffect(() => {
        if (editingRule) {
            formRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        }
    }, [editingRule]);

    return (
        <>
            <div ref={formRef}>
            <AlertRuleForm
                initialRule={editingRule}
                onSaved={() => {
                    setEditingRule(null);
                    setRefreshKey(k => k + 1);
                }}
            />
            </div>

            <AlertRulesList
                onEdit={handleEdit}            
                refreshKey={refreshKey}
            />
        </>
    );
}