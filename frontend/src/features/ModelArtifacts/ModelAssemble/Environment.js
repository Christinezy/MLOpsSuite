import * as React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';

  
  function SelectEnvironment(props) {
    const { env, setEnv } = props;
    const handleChange = (event) => {
      setEnv(event.target.value);
      props.handleDeployInputs("environment", event.target.value);
    };
  
    return (
      <FormControl sx={{ my: 2, minWidth: "100%" }} size="small">
        <InputLabel required={true}>Select environment</InputLabel>
        <Select
          label="Select environment"
          value={env}
          onChange={handleChange}
        >
          <MenuItem value={"Python"}>Python</MenuItem>
        </Select>
      </FormControl>
    );
  }
  
  function SelectStrategy(props) {
    const { strategy, setStrategy } = props;
    const handleChange = (event) => {
      setStrategy(event.target.value);
      props.handleDeployInputs("strategy", event.target.value);
    };
  
    return (
      <FormControl sx={{ my: 2, minWidth: "100%" }} size="small">
        <InputLabel required={true}>Select deployment strategy</InputLabel>
        <Select
          label="Select deployment strategy"
          value={strategy}
          onChange={handleChange}
        >
          <MenuItem value={"direct"}>Direct</MenuItem>
          <MenuItem value={"blue/green"}>Blue/Green</MenuItem>
          <MenuItem value={"canary"}>Canary</MenuItem>
        </Select>
      </FormControl>
    );
  }

export default function Environment(props) {
    return (
        <React.Fragment>
            <Typography variant="h7" sx={{ fontWeight: "bold" }} gutterBottom>
              Environment
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
                <Box 
                  sx={{
                    display: "flex", 
                    flexDirection: "row", 
                    justifyContent: "space-between",
                  }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}>
                    Environment
                  </Typography>
                </Box>
                <SelectEnvironment 
                  handleDeployInputs={props.handleDeployInputs} 
                  env={props.env}
                  setEnv={props.setEnv}
                />
                <Box 
                  sx={{
                    display: "flex", 
                    flexDirection: "row", 
                    justifyContent: "space-between",
                  }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: "bold", mt: 3 }}>
                    Deployment Strategy
                  </Typography>
                </Box>
                <SelectStrategy 
                  handleDeployInputs={props.handleDeployInputs} 
                  strategy={props.strategy}
                  setStrategy={props.setStrategy}
                />
              </CardContent>
            </Card>
        </React.Fragment>
    );
}