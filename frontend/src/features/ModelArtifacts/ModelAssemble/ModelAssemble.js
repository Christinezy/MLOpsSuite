import * as React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { Stack } from "@mui/material";
import Action from "./Action";
import Model from "./Model";
import Environment from "./Environment";
import { useState, useEffect } from "react";

const initial_inputs =
  {
    "version": 1,
    "environment": "",
    "strategy": ""
  }

export default function ModelAssemble() {
  const [state, setState] = useState(1);
  const [inputs, setInputs] = useState(initial_inputs);

  const [env, setEnv] = useState("");
  const [strategy, setStrategy] = useState("");

  useEffect(() => {
    handleDeployInputs("version", 1);
    handleDeployInputs("environment", "");
    handleDeployInputs("strategy", "");
  }, []);

  function handleDeployInputs(key, value) {
    inputs[key] = value;
  }
  
  return (
    <Container sx={{ py: 4 }} maxWidth="xl">
      <Stack spacing={2}>
        <Typography variant="h6" align="left" sx={{ fontWeight: "bold" }}>
          Assemble Model
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Model 
              handleDeployInputs={handleDeployInputs} 
              selectState={setState}
              state={state}
              setEnv={setEnv}
              setStrategy={setStrategy}
            />
          </Grid>
          <Grid item xs={4}>
            <Action 
              inputs={inputs} 
              state={state}
            />
          </Grid>
          <Grid item xs={4}>
            <Environment 
              handleDeployInputs={handleDeployInputs} 
              env={env}
              setEnv={setEnv}
              strategy={strategy}
              setStrategy={setStrategy}
            />
          </Grid>
        </Grid>
      </Stack>
    </Container>
  );
}
