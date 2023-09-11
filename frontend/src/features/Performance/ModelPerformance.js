import * as React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Button from '@mui/material/Button';
import Grid from "@mui/material/Grid";
import TableContainer from '@mui/material/TableContainer';
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";
import { Stack } from "@mui/material";
import Chart from "./Chart";
import Snackbar from '@mui/material/Snackbar';
import PropTypes from "prop-types";
import CardActionArea from "@mui/material/CardActionArea";
import Paper from "@mui/material/Paper";
import FormControl from '@mui/material/FormControl';
import Alert from '@mui/material/Alert';
import TextField from '@mui/material/TextField';
import RefreshIcon from '@mui/icons-material/Refresh';
import { LoadingButton } from "@mui/lab";
import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { 
  retrievePerformanceThunk, 
  submitSelectionThunk,
  getThresholdThunk,
  updateThresholdThunk
} from "./slicePerformance";
import { retrieveProjectThunk } from "../sliceProject"
import { selectProject } from "../projectSelectors";


const projectId = window.location.href.substring(window.location.href.length - 1);
const role = localStorage.getItem("role");

function metricsArray(metrics) {
  let rows = [
    {
      id: 1,
      title: "Total Predictions",
      number: metrics.total_prediction,
    },
    {
      id: 2,
      title: "Total Requests",
      number: metrics.total_requests,
    },
    {
      id: 3,
      title: "Number of Containers",
      number: metrics.num_containers,
    },
    {
      id: 4,
      title: "CPU Usage",
      number: metrics.cpu_usage,
    },
    {
      id: 5,
      title: "RAM Usage",
      number: metrics.ram_usage,
    }
  ];
  return rows;
}

function Metrics(props) {
  const { metric } = props;
  return (
    <Grid item xs={2.4}>
      <CardActionArea
        component="a"
        onClick={() => props.switchContent(metric.id)}
      >
        <Card sx={{ display: "flex" }}>
          <CardContent sx={{ flex: 1 }}>
            <Typography
              variant="subtitle1"
              color="text.secondary"
              sx={{ textAlign: "center" }}
            >
              {metric.title}
            </Typography>
            <Typography variant="h4" sx={{ textAlign: "center" }}>
              {metric.number}
            </Typography>
          </CardContent>
        </Card>
      </CardActionArea>
    </Grid>
  );
}

Metrics.propTypes = {
  metric: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    number: PropTypes.string.isRequired,
  }).isRequired,
};

function SelectNodes() {
  const [min, setMin] = React.useState("");
  const [max, setMax] = React.useState("");
  const [desired, setDesired] = React.useState("");
  const [open, setOpen] = React.useState(false);
  const dispatch = useDispatch();
  const error_message = useSelector((state) => state.performance.error_message);
  const success = useSelector((state) => state.performance.success);

  const handleSubmit = (event) => {
    event.preventDefault();
    dispatch(
      submitSelectionThunk({
        id: projectId,
        payload: {
          "min_nodes": min,
          "max_nodes": max,
          "desired_nodes": desired 
        }
      })
    );
    setOpen(true);
  };

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    } 
    setOpen(false);
  };

  return (
    <React.Fragment>
      {
        success && !error_message &&
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={open}
          autoHideDuration={3000} 
          onClose={handleClose}
        >
          <Alert variant="filled" onClose={handleClose} severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        </Snackbar>
      }
      {
        error_message &&
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={open} 
          autoHideDuration={3000} 
          onClose={handleClose}
        >
          <Alert variant="filled" onClose={handleClose}  severity="error" sx={{ width: '100%' }}>
            {error_message}
          </Alert>
        </Snackbar>
      }

      <Grid item xs={1.5}>
        <FormControl fullWidth>
          <TextField
            type="number"
            value={min}
            label="Minimum Nodes"
            pattern="[^0-9]*"
            size="small"
            onChange={(e) => {
              if (e.target.validity.valid || e.target.value === "") {
                let val = parseInt(e.target.value);
                val = val < 1 ? 1 : val;
                setMin(val);
              }
            }}
            onBlur={(e) => {
              let val = parseInt(e.target.value);
              // Check max
              if (val > max) setMax(val);
              // Check desired
              if (val > desired) setDesired(val);
            }}
            inputProps={{ min: 1 }}
          />
        </FormControl>
      </Grid>
      <Grid item xs={1.5}> 
        <FormControl fullWidth>
          <TextField
            type="number"
            value={max}
            label="Maximum Nodes"
            pattern="[^0-9]*"
            size="small"
            onChange={(e) => {
              if (e.target.validity.valid || e.target.value === "") {
                let val = parseInt(e.target.value);
                val = val < 1 ? 1 : val;
                setMax(val);
              }
            }}
            onBlur={(e) => {
              if (e.target.validity.valid || e.target.value === "") {
                let val = parseInt(e.target.value);
                if (val < min) setMax(min);
                // Check desired
                if (val < min && desired > val) {
                  setDesired(min);
                } else if (desired > val) {
                  setDesired(val);
                }
              }
            }}
            inputProps={{ min: 1 }}
          />
        </FormControl>
      </Grid>
      <Grid item xs={1.5}> 
        <FormControl fullWidth>
          <TextField
            type="number"
            value={desired}
            label="Desired Nodes"
            pattern="[^0-9]*"
            size="small"
            onChange={(e) => {
              if (e.target.validity.valid || e.target.value === "") {
                let val = parseInt(e.target.value);
                setDesired(val);
              }
            }}
            onBlur={(e) => {
              if (e.target.validity.valid || e.target.value === "") {
                let val = parseInt(e.target.value);
                if (val > max) {
                  setDesired(max);
                } else if (val < min) {
                  setDesired(min);
                } else {
                  setDesired(val);
                }
              }
            }}
            inputProps={{ min: 1}}
          />
        </FormControl>
      </Grid>
      <Grid item xs={1.5}>
        <Button 
          variant="outlined" 
          sx={{ height: "40px", textTransform: "None" }}
          onClick={handleSubmit}
          size="small"
        >
          Elastic Scaling
        </Button>
      </Grid>

    </React.Fragment>
  );
}

function SetThreshold(props) {
  const dispatch = useDispatch();
  const { threshold, setThreshold } = props;
  const [open, setOpen] = React.useState(false);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    } 
    setOpen(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    dispatch(updateThresholdThunk({ 
      id: projectId, 
      payload: parseFloat(threshold).toFixed(1)
      }
    ));
    setOpen(true);
  };

  const handleBlur = (event) => {
    let val = parseFloat(event.target.value);
    if (val < 0) {
      setThreshold(0);
    } else if (val > 100) {
      setThreshold(100);
    }
  }

  const handleChange = (event) => {
    let val = parseFloat(event.target.value);
    setThreshold(val);
  }

  return (
    <React.Fragment>
      <Snackbar 
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        open={open}
        autoHideDuration={3000} 
        onClose={handleClose}
      >
        <Alert variant="filled" onClose={handleClose} severity="success" sx={{ width: '100%' }}>
          Successfully set CPU usage threshold.
        </Alert>
      </Snackbar>
      <Grid item xs={1.8}>
        <FormControl fullWidth>
          <TextField
            type="number"
            value={threshold}
            label="CPU Usage Threshold"
            size="small"
            onChange={handleChange}
            onBlur={handleBlur}
          />
        </FormControl>
      </Grid>      
      <Grid item xs={1.5}>
        <Button 
          variant="outlined" 
          sx={{ height: "40px", textTransform: "None" }}
          onClick={handleSubmit}
          size="small"
        >
          Set Threshold
        </Button>
      </Grid>
    </React.Fragment>
  );
}


function CurrentNodesTable() {
  const modelId = window.location.href.substring(window.location.href.length - 1);

  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(retrieveProjectThunk(modelId));
  }, [dispatch, modelId]);

  const project = useSelector(selectProject);

  return (
    <TableContainer>
      <Table sx={{ minWidth: 650, mt: 2 }} aria-label="simple table">
        <TableHead>
            <TableRow >
            <TableCell sx={{ fontWeight: "bold" }}>Model Name & Description</TableCell>
            <TableCell  align="center" sx={{ fontWeight: "bold" }}>Status</TableCell>
            <TableCell  align="center" sx={{ fontWeight: "bold" }}>Created</TableCell>
            <TableCell  align="center" sx={{ fontWeight: "bold" }}>Minimum Nodes</TableCell>
            <TableCell  align="center" sx={{ fontWeight: "bold" }}>Maximum Nodes</TableCell>
            <TableCell  align="center" sx={{ fontWeight: "bold" }}>Desired Nodes</TableCell>
            </TableRow>
        </TableHead>
        <TableBody>
            <TableRow sx={{ bgcolor: "#f5f5f5" }}>
                <TableCell component="th" scope="row">
                    <ListItem component="div" disablePadding>
                        <ListItemText 
                            primary={project.project_name} 
                            secondary={project.description} 
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
                    {project.status}  
                </TableCell>
                <TableCell align="center">
                    {project.date_created? project.date_created.slice(5,-4):""}
                </TableCell>
                <TableCell align="center">
                    {project.min_num_nodes}
                </TableCell>
                <TableCell align="center">
                    {project.max_num_nodes}
                </TableCell>
                <TableCell align="center">
                    {project.desired_num_nodes}
                </TableCell>
            </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
    );
  }


export default function ModelPerformance() {
  // switch chart
  const [content, setContent] = useState(1);
  const switchContent = (selector) => {
    setContent(() => selector);
  };

  // load perfprmance metrics
  const dispatch = useDispatch();
  useEffect(() => {
      dispatch(retrievePerformanceThunk(projectId));
      dispatch(getThresholdThunk(projectId));
  }, [dispatch, projectId]);   

  const performance = useSelector((state) => state.performance);
  const data = useSelector((state) => state.performance.threshold);
  const [threshold, setThreshold] = useState("");

  // get loading actions
  const loadingPerformance = useSelector(
    (state) => state.performance.loadingPerformance
    );
  const loadingProject = useSelector(
    (state) => state.project.loadingProject
    );
  const loadingGetThreshold = useSelector(
    (state) => state.performance.loadingGetThreshold
    );

  // get chart data
  const total_prediction_chart = useSelector(
    (state) => state.performance.total_prediction_chart
    );
  const total_requests_chart = useSelector(
    (state) => state.performance.total_requests_chart
    );
  const num_containers_chart = useSelector(
    (state) => state.performance.num_containers_chart
    );
  const cpu_usage_chart = useSelector(
    (state) => state.performance.cpu_usage_chart
    );
  const ram_usage_chart = useSelector(
    (state) => state.performance.ram_usage_chart
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
          loading={loadingPerformance || loadingProject || loadingGetThreshold}
          onClick={() => {
            dispatch(retrievePerformanceThunk(projectId));
            dispatch(retrieveProjectThunk(projectId));
            dispatch(getThresholdThunk(projectId));
          }}
        >
          <RefreshIcon />
        </LoadingButton>
      </Box>
      <Container sx={{ py: 1 }} maxWidth="xl">
        <CurrentNodesTable />
        <Stack spacing={4} sx={{ mt: 4 }}>
          <Grid container spacing={2}>
            {(role == "Admin" || role == "MLOps Engineer") &&
              <SelectNodes />
            }
            {(role == "Manager" || role == "Admin" || role == "MLOps Engineer") &&
              <SetThreshold 
                threshold={threshold}
                setThreshold={setThreshold}
              />
            }
          </Grid>
          <Grid container spacing={2} alignItems="center">
            {metricsArray(performance).map((metric) => (
              <Metrics
                key={metric.id}
                metric={metric}
                switchContent={switchContent}
              />
            ))}
          </Grid>
          <Grid item xs={12} md={8} lg={9}>
            <Paper
              sx={{
                p: 2,
                display: "flex",
                flexDirection: "column",
                height: 360,
              }}
            >
              {content === 1 && <Chart title="Total Predictions" data={total_prediction_chart} />}
              {content === 2 && <Chart title="Total Requests" data={total_requests_chart} />}
              {content === 3 && (
                <Chart title="Number of Containers" data={num_containers_chart} />
              )}
              {content === 4 && 
                <Chart title="CPU Usage" 
                  data={cpu_usage_chart} 
                  domain={[0,100]}
                  threshold={data}
                />
              }
              {content === 5 && (
                <Chart title="RAM Usage" data={ram_usage_chart} />
              )}
            </Paper>
          </Grid>
        </Stack>
      </Container>
    </React.Fragment>

  );
}
