import * as React from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import ModelOverview from "./ModelOverview";
import ModelPerformace from "./Performance/ModelPerformance";
import ModelArtifacts from "./ModelArtifacts/ModelArtifacts";
import DriftMetrics from "./DataDrift/DriftMetrics";
import Requests from "./Requests";
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    "aria-controls": `simple-tabpanel-${index}`,
  };
}

export default function ModelManager() {
  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: "100%" }}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={value}
          onChange={handleChange}
          aria-label="basic tabs example"
        >
          <Tab label="Overview" {...a11yProps(0)} />
          <Tab label="Drift Monitoring" {...a11yProps(1)} />
          <Tab label="Performance" {...a11yProps(2)} />
          <Tab label="Model Artifacts" {...a11yProps(3)} />
          <Tab label="Requests" {...a11yProps(4)} />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <ModelOverview />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <DriftMetrics />
      </TabPanel>
      <TabPanel value={value} index={2}>
        <ModelPerformace />
      </TabPanel>
      <TabPanel value={value} index={3}>
        <ModelArtifacts />
      </TabPanel>
      <TabPanel value={value} index={4}>
        <Requests />
      </TabPanel>
    </Box>
  );
}
