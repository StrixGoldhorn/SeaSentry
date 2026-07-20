import { update_AOI } from "./utils";

export function AOIEditSidebar({
    editingAOI,
    coords,
    finish,
    cancel
}) {

    async function handleFinish() {
        await update_AOI({
            aoi_id:editingAOI.area_of_interest_id,
            coords:coords
        });
        finish();
    }

    return (
        <div>
            <h2>Edit AOI</h2>
            <p>
                {editingAOI.area_of_interest_name}
            </p>

            <button onClick={handleFinish}>
                Finish Editing
            </button>

            <button onClick={cancel}>
                Cancel
            </button>
        </div>
    );
}