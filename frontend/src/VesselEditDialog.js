import { useState } from "react";

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from "@mui/material";

import { update_ship_using_data_id } from "./utils";

export default function VesselEditDialog({
  ship,
  onClose,
  onSaved,
}) {
  const [name, setName] = useState(ship.ship_name ?? "");
  const [type, setType] = useState(ship.ship_type ?? "");
  const [flag, setFlag] = useState(ship.flag ?? "");

  const [length, setLength] =
    useState(ship.length_meters ?? "");

  const [beam, setBeam] =
    useState(ship.beam_meters ?? "");

  const [tags, setTags] = useState(
    ship.user_tags?.join(", ") ?? ""
  );

  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);

    await update_ship_using_data_id({
      vessel_data_id: ship.vessel_data_id,

      ship_name:
        name !== ship.ship_name ? name : null,

      ship_type:
        type !== ship.ship_type ? type : null,

      flag:
        flag !== ship.flag ? flag : null,

      length_meters:
        Number(length) !== ship.length_meters
          ? Number(length)
          : null,

      beam_meters:
        Number(beam) !== ship.beam_meters
          ? Number(beam)
          : null,

      user_tags:
        JSON.stringify(tags.split(",").map(x => x.trim()).filter(Boolean))
        !==
        JSON.stringify(ship.user_tags ?? [])
          ? tags
              .split(",")
              .map(x => x.trim())
              .filter(Boolean)
          : null,
    });

    setSaving(false);

    onSaved();
  }

  return (
    <Dialog
      open
      onClose={onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>Edit Vessel</DialogTitle>

      <DialogContent>

        <TextField
          margin="normal"
          label="Ship Name"
          fullWidth
          value={name}
          onChange={e => setName(e.target.value)}
        />

        <TextField
          margin="normal"
          label="Ship Type"
          fullWidth
          value={type}
          onChange={e => setType(e.target.value)}
        />

        <TextField
          margin="normal"
          label="Flag"
          fullWidth
          value={flag}
          onChange={e => setFlag(e.target.value)}
        />

        <TextField
          margin="normal"
          type="number"
          label="Length"
          fullWidth
          value={length}
          onChange={e => setLength(e.target.value)}
        />

        <TextField
          margin="normal"
          type="number"
          label="Beam"
          fullWidth
          value={beam}
          onChange={e => setBeam(e.target.value)}
        />

        <TextField
          margin="normal"
          label="User Tags"
          helperText="Comma separated"
          fullWidth
          value={tags}
          onChange={e => setTags(e.target.value)}
        />

      </DialogContent>

      <DialogActions>

        <Button onClick={onClose}>
          Cancel
        </Button>

        <Button
          variant="contained"
          onClick={save}
          disabled={saving}
        >
          Save
        </Button>

      </DialogActions>

    </Dialog>
  );
}