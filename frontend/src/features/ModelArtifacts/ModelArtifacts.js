import * as React from "react";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { styled } from "@mui/material/styles";
import RefreshIcon from '@mui/icons-material/Refresh';
import { LoadingButton } from "@mui/lab";
import ModelAssemble from "./ModelAssemble/ModelAssemble";
import ModelVersions from "./ModelVersions";
import DeployedModels from "./DeployedModels/DeployedModels";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  retrieveVersionsThunk,
  retrieveActiveVersionThunk,
  retrieveManagerListThunk,
} from "./sliceVersion";

const projectId = window.location.href.substring(
  window.location.href.length - 1
);

const StyledTab = styled((props) => <Tab disableRipple {...props} />)(
  ({ theme }) => ({
    textTransform: "none",
    fontWeight: theme.typography.fontWeightRegular,
    fontSize: theme.typography.pxToRem(14),
    marginRight: theme.spacing(1),
  })
);

const role = localStorage.getItem("role");

function ModelSummary() {
  const active_status = useSelector((state) => state.version.active_status);
  const data = useSelector((state) => state.version.active_data);
  return (
    <TableContainer>
      <Table sx={{ minWidth: 650, mt: 2 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: "bold" }}>
              Model Name & Description
            </TableCell>
            <TableCell align="center" sx={{ fontWeight: "bold" }}>
              Status
            </TableCell>
            {active_status == "true" && <React.Fragment></React.Fragment>}
            <TableCell align="center" sx={{ fontWeight: "bold" }}>
              Created
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow sx={{ bgcolor: "#f5f5f5" }}>
            <TableCell component="th" scope="row">
              <ListItem component="div" disablePadding>
                <ListItemText
                  primary={data.model_name}
                  secondary="testing"
                  primaryTypographyProps={{
                    fontSize: 14,
                    fontWeight: "bold",
                    mt: -1,
                  }}
                  secondaryTypographyProps={{
                    fontSize: 14,
                    mb: -1,
                  }}
                />
              </ListItem>
            </TableCell>
            <TableCell align="center">
              {active_status == "true" ? "Live" : "Down"}
            </TableCell>
            {active_status == "true" && <React.Fragment></React.Fragment>}
            <TableCell align="center">
              {data.model_created_time.slice(5, -4)}
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default function ModelArtifacts() {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(retrieveVersionsThunk(projectId));
    dispatch(retrieveActiveVersionThunk(projectId));
    dispatch(retrieveManagerListThunk(projectId));
  }, [dispatch, projectId]);

  // switch between Assemble and Version
  const [value, setValue] = React.useState("1");
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const loadingVersions = useSelector(
    (state) => state.version.loadingVersions
    );
  const loadingActiveVersion = useSelector(
    (state) => state.version.loadingActiveVersion
    );
  const loadingManagerList = useSelector(
    (state) => state.version.loadingManagerList
    );

  return (
    <React.Fragment>
      <Box 
        sx={{
          display: "flex",
          justifyContent: "right", 
          mt: 2 
        }}
      >
        <LoadingButton
          loading={loadingVersions || loadingActiveVersion || loadingManagerList}
          onClick={() => {
            dispatch(retrieveVersionsThunk(projectId));
            dispatch(retrieveActiveVersionThunk(projectId));
            dispatch(retrieveManagerListThunk(projectId));
          }}
        >
          <RefreshIcon />
        </LoadingButton>
      </Box>
      <ModelSummary />
      <Box sx={{ width: "100%", bgcolor: "background.paper" }}>
        <Tabs value={value} onChange={handleChange}>
          <StyledTab label="Deployed Models" value="1" />
          {role !== "Manager" && <StyledTab label="Assemble" value="2" />}
          <StyledTab label="Versions" value="3" />
        </Tabs>
      </Box>
      {value == 1 && <DeployedModels />}
      {value == 2 && role !== "Manager" && <ModelAssemble />}
      {value == 3 && <ModelVersions />}
    </React.Fragment>
  );
}
