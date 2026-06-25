import AlertRulePanel from "./AlertRuleForm";
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
            <NavigateToMapButton/>
        </div>
    )
}