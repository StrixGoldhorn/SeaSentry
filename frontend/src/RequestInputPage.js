import AlertRulePanel from "./AlertRuleForm";
import AlertRulesList from "./AlertRulesDisplay";
import AOIPanel from "./AOIForm";
import GeofencePanel from "./GeofenceForm";
import { NavigateToMapButton } from "./NavigateButtons";
import VOIList from "./VOIDisplay";
import VOIPanel from "./VOIForm";

export function RequestInputPage () {
    return (
        <div>
            <AOIPanel/>
            <GeofencePanel/>
            <VOIPanel/>
            <VOIList/>
            <AlertRulePanel/>
            <AlertRulesList/>
            <NavigateToMapButton/>
        </div>
    )
}