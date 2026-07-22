import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Button, Stack } from "@mui/material";

const SHIP_TYPES = [
  "Cargo", "Fishing", "High Speed Craft", "Law Enforcement",
  "Medical Transport", "Military", "Passenger", "Pleasure Craft",
  "Sailing", "SAR", "Tanker", "Tug"
];

export default function FilterSidebar({ 
  selectedShiptype, 
  setSelectedShiptype, 
  appliedShiptype, 
  setAppliedShiptype 
}) {
  const handleApply = () => {
    setAppliedShiptype(selectedShiptype);
  };

  const handleClear = () => {
    setSelectedShiptype("");
    setAppliedShiptype("");
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Filter Vessels
      </Typography>
      
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="shiptype-filter-label">Ship Type</InputLabel>
        <Select
          labelId="shiptype-filter-label"
          id="shiptype-filter"
          value={selectedShiptype}
          label="Ship Type"
          onChange={(e) => setSelectedShiptype(e.target.value)}
        >
          <MenuItem value=""><em>All</em></MenuItem>
          {SHIP_TYPES.map((type) => (
            <MenuItem key={type} value={type}>{type}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <Stack direction="row" spacing={2}>
        <Button variant="contained" color="primary" onClick={handleApply} fullWidth>
          Apply
        </Button>
        <Button variant="outlined" color="secondary" onClick={handleClear} fullWidth>
          Clear
        </Button>
      </Stack>
      
      {appliedShiptype && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Currently filtering by: <strong>{appliedShiptype}</strong>
        </Typography>
      )}
    </Box>
  );
}