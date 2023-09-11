import * as React from "react";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { Stack } from "@mui/material";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import StepContent from "@mui/material/StepContent";
import { useDispatch, useSelector } from "react-redux";
import { useEffect, useState } from "react";
import { retrieveProjectThunk, retrieveVersionThunk } from "./sliceProject";
import { selectProject } from "./projectSelectors";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorRoundedIcon from "@mui/icons-material/ErrorRounded";

export default function ModelOverview() {
  const modelId = window.location.href.substr(window.location.href.length - 1);

  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(retrieveProjectThunk(modelId));
    dispatch(retrieveVersionThunk(modelId));
  }, [dispatch, modelId]);

  const [expandStep, setExpandStep] = useState(true);

  const project = useSelector(selectProject);
  const versions = project.versions;

  return (
    <Container sx={{ py: 4 }} maxWidth="xl">
      <Stack spacing={2}>
        <Typography variant="subtitle1" align="left" color="text.secondary">
          Understand the purpose, content, and the history of the deployment.
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Typography variant="h7" sx={{ fontWeight: "bold" }} gutterBottom>
              Summary
            </Typography>
            <Card
              sx={{
                marginTop: 1,
                height: "100%",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <CardContent>
                <Stack spacing={1}>
                  <Typography variant="subtitle2" color="gray">
                    Name
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.project_name}
                  </Typography>
                  <Typography variant="subtitle2" color="gray">
                    Description
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.description}
                  </Typography>
                  <Typography variant="subtitle2" color="gray">
                    Endpoint
                  </Typography>
                  {project.status === "Live" && (
                    <Typography noWrap variant="subtitle2">
                      {project.endpoint}
                    </Typography>
                  )}
                  <Typography variant="subtitle2" color="gray">
                    Status
                  </Typography>
                  <Typography variant="subtitle2">{project.status}</Typography>
                  <Typography variant="subtitle2" color="gray">
                    Owner
                  </Typography>
                  <Typography variant="subtitle2">{project.owner}</Typography>
                  {/* <Typography variant="subtitle2" color="gray">
                    Approval status
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.approval_status}
                  </Typography> */}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="h7" sx={{ fontWeight: "bold" }} gutterBottom>
              Content
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
                <Stack spacing={1}>
                  <Typography variant="subtitle2" color="gray">
                    Build Environment
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.build_environment}
                  </Typography>

                  <Typography variant="subtitle2" color="gray">
                    Model Age
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.model_age} days
                  </Typography>
                  <Typography variant="subtitle2" color="gray">
                    Drift
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.drift === "Ok" ? (
                      <CheckCircleIcon
                        sx={{ color: "#4caf50", fontSize: "20px" }}
                      />
                    ) : (
                      <ErrorRoundedIcon
                        sx={{ color: "#ef5350", fontSize: "20px" }}
                      />
                    )}
                  </Typography>
                  <Typography variant="subtitle2" color="gray">
                    Performance
                  </Typography>
                  <Typography variant="subtitle2">
                    {project.performance === "Ok" ? (
                      <CheckCircleIcon
                        sx={{ color: "#4caf50", fontSize: "20px" }}
                      />
                    ) : (
                      <ErrorRoundedIcon
                        sx={{ color: "#ef5350", fontSize: "20px" }}
                      />
                    )}
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="h7" sx={{ fontWeight: "bold" }} gutterBottom>
              Governance
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
                <Box sx={{ maxWidth: 400 }}>
                  <Stepper activeStep={4} orientation="vertical">
                    {versions.map((version) => (
                      <Step
                        active={expandStep ? false : true}
                        key={version.version_number}
                      >
                        <StepLabel
                          error={
                            version.approval_status === "not approved" ||
                            version.approval_status === "pending approval" ||
                            version?.test_status === "not passed"
                          }
                          optional={
                            <>
                              <Typography variant="caption">
                                {version.created_time}
                              </Typography>
                              <Typography variant="subtitle2">
                                {version.description}
                              </Typography>
                            </>
                          }
                        >
                          <Typography
                            sx={{ fontWeight: "bold" }}
                            variant="subtitle2"
                          >
                            Version {version.version_number}
                          </Typography>
                        </StepLabel>

                        <StepContent>
                          {version.request[0]?.who_sumbit_request && (
                            <Typography variant="body2">
                              Requested by{" "}
                              {version.request[0].who_sumbit_request}
                            </Typography>
                          )}
                          {version.request[0]?.submit_request_comment && (
                            <Typography
                              sx={{ fontStyle: "italic" }}
                              variant="body2"
                              color="grey"
                            >
                              {version.request[0].submit_request_comment}
                            </Typography>
                          )}
                          {version.request[0] && (
                            <Typography>---------</Typography>
                          )}
                          {version.approval_status === "approved" ? (
                            <Typography variant="subtitle2">
                              {version.request[0]?.who_handle_request} approved
                            </Typography>
                          ) : version.approval_status === "pending approval" ? (
                            <Typography variant="subtitle2" color="red">
                              Pending {version.request[0]?.who_handle_request}'s
                              approval
                            </Typography>
                          ) : (
                            <Typography variant="subtitle2" color="red">
                              {version.request[0]?.who_handle_request} did not
                              approved
                            </Typography>
                          )}
                          {version.request[0]?.handle_request_comment && (
                            <Typography
                              sx={{ fontStyle: "italic" }}
                              variant="body2"
                              color="grey"
                            >
                              {version.request[0].handle_request_comment}
                            </Typography>
                          )}
                          {version.request[0] && (
                            <Typography>---------</Typography>
                          )}

                          {version?.deploy_status === "deployed" ? (
                            <Typography variant="subtitle2">
                              Deployed by {version?.who_deloy} with{" "}
                              {version?.traffic_percentage}% traffic
                            </Typography>
                          ) : (
                            <Typography variant="subtitle2">
                              Not deployed yet
                            </Typography>
                          )}
                          {version?.test_status && (
                            <Typography
                              variant="subtitle2"
                              color={
                                version?.test_status === "not passed"
                                  ? "red"
                                  : "green"
                              }
                            >
                              {version?.test_status === "test passed"
                                ? "Tests passed"
                                : "Tests failed"}
                            </Typography>
                          )}
                        </StepContent>
                      </Step>
                    ))}
                    <Button onClick={() => setExpandStep(!expandStep)}>
                      {expandStep ? "Detailed View" : "Summary View"}
                    </Button>
                  </Stepper>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Stack>
    </Container>
  );
}
