import * as React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import PropTypes from "prop-types";
import AddIcon from "@mui/icons-material/Add";
import Button from "@mui/material/Button";
import { ActiveDeployments, Summary } from "./Summary";
import { GovernanceInventory } from "./Governance";
import { PredictionHealthInventory } from "./PredictionHealth";
import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { retrieveProjectlistThunk } from "./sliceProjectlist";
import ProjectCreationModal from "./ProjectCreationModal";


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
            {value === index && (
                <Box sx={{ p: 3 }}>
                    <Typography>{children}</Typography>
                </Box>
            )}
        </div>
    );
}

TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
};

function a11yProps(index) {
    return {
        id: `simple-tab-${index}`,
        "aria-controls": `simple-tabpanel-${index}`,
    };
}

function BasicTabs(props) {
    const [value, setValue] = React.useState(0);

    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    return (
        <Box sx={{ width: "100%" }}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                    <Tab label="Governance" {...a11yProps(0)} />
                    <Tab label="Prediction Health" {...a11yProps(1)} />
                </Tabs>
            </Box>
            <TabPanel value={value} index={0}>
                <GovernanceInventory data={props.data} />
            </TabPanel>
            <TabPanel value={value} index={1}>
                <PredictionHealthInventory data={props.data} />
            </TabPanel>
        </Box>
    );
}

export default function Deployments() {
    const [modalOpen, setModalOpen] = useState(false);
    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(retrieveProjectlistThunk());
    }, [dispatch]);
    const projectlist = useSelector((state) => state.projectlist);
    const projects = projectlist.projects;
    const performanceSummary = useSelector((state) => state.projectlist.performanceSummary);
    const driftSummary = useSelector((state) => state.projectlist.driftSummary);
    return (
        <Box
            component="main"
            sx={{
                flexGrow: 1,
                height: "100vh",
                overflow: "auto",
            }}
        >
            <ProjectCreationModal open={modalOpen} handleClose={() => setModalOpen(false)} />
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Grid container spacing={3}>
                    <Grid item xs={4}>
                        <Paper
                            sx={{
                                p: 2,
                                display: "flex",
                                flexDirection: "column",
                                height: 180,
                            }}
                            elevation={2}
                        >
                            <ActiveDeployments />
                        </Paper>
                    </Grid>

                    <Grid item xs={4}>
                        <Paper
                            sx={{
                                p: 2,
                                display: "flex",
                                flexDirection: "column",
                                height: 180,
                            }}
                            elevation={2}
                        >
                            <Summary
                                title="Performance Monitoring Summary"
                                data={performanceSummary}
                            />
                        </Paper>
                    </Grid>
                    <Grid item xs={4}>
                        <Paper
                            sx={{
                                p: 2,
                                display: "flex",
                                flexDirection: "column",
                                height: 180,
                            }}
                            elevation={2}
                        >
                            <Summary title="Data Drift Summary" data={driftSummary} />
                        </Paper>
                    </Grid>
                    <Box
                        sx={{
                            display: "flex",
                            justifyContent: "right",
                            width: "100%",
                            mt: 3,
                            mb: -3,
                        }}
                    >
                        <Button
                            color="primary"
                            startIcon={<AddIcon />}
                            onClick={() => setModalOpen(true)}
                        >
                            New Project
                        </Button>
                    </Box>
                    <Grid item xs={12}>
                        <Paper
                            sx={{ p: 2, display: "flex", flexDirection: "column" }}
                            elevation={2}
                        >
                            <BasicTabs data={projects} />
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
}
