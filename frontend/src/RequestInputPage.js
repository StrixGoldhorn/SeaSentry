import AlertRulePanel from "./AlertRuleForm";
import AlertRulesList from "./AlertRulesDisplay";
import AOIPanel from "./AOIForm";
import GeofencePanel from "./GeofenceForm";
import { NavigateToMapButton } from "./NavigateButtons";
import VOIPanel from "./VOIForm";

export function RequestInputPage () {
    return (
        <div>
            <AOIPanel/>
            <GeofencePanel/>
            <VOIPanel/>
            <AlertRulePanel/>
            <AlertRulesList/>
            <NavigateToMapButton/>
        </div>
    )
}