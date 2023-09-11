import * as React from "react";
import { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { MenuItem, Stack, TextField } from "@mui/material";
import { FeatureDriftImportance } from "./FeatureDriftImportance";
import { FeatureDetails } from "./FeatureDetails";

export default function DataDrift() {
  const [feature, setFeature] = useState("Grade");

  const handleChange = (event) => {
    setFeature(event.target.value);
  };
  return (
    <Container sx={{ py: 8 }} maxWidth="xl">
      <Grid direction="row" alignItems="center" container spacing={5}>
        <Grid item xs={6}>
          <Typography variant="h7" sx={{ fontWeight: "bold" }}>
            Feature Drift vs Feature Importance
          </Typography>
          <Card
            sx={{
              marginTop: 1,
              height: "100%",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <CardContent sx={{ flexGrow: 1 }}>
              <FeatureDriftImportance />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6}>
          <Stack direction="row" alignItems="center" spacing={2}>
            <Typography variant="h7" sx={{ fontWeight: "bold" }}>
              Feature Details
            </Typography>
            <TextField
              select
              size="small"
              value={feature}
              label="feature"
              onChange={handleChange}
            >
              <MenuItem value={"Grade"}>Grade</MenuItem>
              <MenuItem value={"Location"}>Location</MenuItem>
            </TextField>
          </Stack>

          <Card
            sx={{
              marginTop: 1,
              height: "100%",
            }}
          >
            <FeatureDetails />
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
