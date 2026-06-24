import AOIPanel from "./AOIForm";
import GeofencePanel from "./GeofenceForm";
import VOIPanel from "./VOIForm";

export function RequestInputPage () {
    return (
        <div>
            <AOIPanel/>
            <GeofencePanel/>
            <VOIPanel/>
        </div>
    )
}