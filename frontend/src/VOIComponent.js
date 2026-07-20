import VOIPanel from "./VOIForm";
import VOIList from "./VOIDisplay";
import { useRef, useState } from "react";

export default function VOIComponent () {
    const formRef = useRef();
    const [editingVOI, setEditingVOI] = useState(null);
    const [refreshKey, setRefreshKey] = useState(0);

    return (
        <>
        <div ref={formRef}>
            <VOIPanel
                initialVOI={editingVOI}
                onSaved={() => {
                    setEditingVOI(null);
                    setRefreshKey(v => v + 1);
                }}
            />
        </div>

        <VOIList
            refreshKey={refreshKey}
            onEdit={(voi) => {

                setEditingVOI(voi);

                setTimeout(() => {

                    formRef.current?.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                    });

                }, 0);

            }}
        />
        </>
    )
}