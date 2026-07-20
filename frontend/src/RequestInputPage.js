import './styles.css';
import AOIPanel from "./AOIForm";
import GeofencePanel from "./GeofenceForm";
import { NavigateToMapButton } from "./NavigateButtons";
import VOIList from "./VOIDisplay";
import VOIPanel from "./VOIForm";
import AlertRulesComponent from './AlertRulesComponent';
import VOIComponent from './VOIComponent';

export function RequestInputPage () {
    return (
        <div>
            <AOIPanel/>
            <GeofencePanel/>
            <VOIComponent/>
            <AlertRulesComponent/>
            <NavigateToMapButton/>
        </div>
    )
}