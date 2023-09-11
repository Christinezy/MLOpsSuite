import * as React from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { Stack, Box } from "@mui/material";
import { styled } from "@mui/material/styles";
import { tableCellClasses } from "@mui/material/TableCell";
import Paper from "@mui/material/Paper";
import { useDispatch, useSelector } from "react-redux";
import { retrieveRequestsThunk, resetReview } from "./sliceProject";
import { useEffect, useState } from "react";
import { LoadingButton } from "@mui/lab";
import RefreshIcon from '@mui/icons-material/Refresh';
import ApprovalModal from "./ApprovalModal";
import { selectDataDriftLatest } from "./sliceDataDrift";
import { Alert, IconButton } from "@mui/joy";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    color: theme.palette.common.black,
    fontSize: 14,
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  "&:nth-of-type(odd)": {
    backgroundColor: theme.palette.action.hover,
  },
  // hide last border
  "&:last-child td, &:last-child th": {
    border: 0,
  },
}));

function RequestTable() {
  const dispatch = useDispatch();
  const modelId = window.location.href.substr(window.location.href.length - 1);
  useEffect(() => {
    dispatch(retrieveRequestsThunk(modelId));
  }, [dispatch, modelId]);

  const requests = useSelector(
    (state) => state?.project?.requests?.pending_requests
  );

  const currentVersion = useSelector(
    (state) => state?.project?.requests?.active_version_list[0]
  );

  const [modalOpen, setModalOpen] = useState(false);
  const [description, setDescription] = useState("");
  const [version, setVersion] = useState(0);

  const latestDrift = useSelector(selectDataDriftLatest);
  const loadingRequests = useSelector(
    (state) => state.project.loadingRequests
    );

  const handleOpen = (version, description) => {
    setVersion(version);
    setDescription(description);
    setModalOpen(true);
  };

  const acceptedManagerialRoles = ["Admin", "Manager"];
  const role = localStorage.getItem("role");

  return (
    <React.Fragment>
      <Box 
        sx={{
          display: "flex",
          justifyContent: "right", 
        }}
      >
        <LoadingButton
          loading={loadingRequests}
          onClick={() => {
            dispatch(retrieveRequestsThunk(modelId));
          }}
        >
          <RefreshIcon />
        </LoadingButton>
      </Box>
      <ApprovalModal
        modelId={modelId}
        open={modalOpen}
        description={description}
        version={version}
        handleClose={() => setModalOpen(false)}
      />

      <Typography sx={{ fontWeight: "bold" }} variant="subtitle1">
        Current Version Details
      </Typography>
      {/* <Grid container spacing={2} justifyContent="center"> */}
      <Table>
        <TableBody>
          <StyledTableRow>
            <StyledTableCell sx={{ fontWeight: "bold" }}>
              Version
            </StyledTableCell>

            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Status
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Log Loss
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              AUC ROC
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              KS Score
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Gini Norm
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Rate Top 10
            </StyledTableCell>
          </StyledTableRow>
          {currentVersion && (
            <StyledTableRow>
              <TableCell align="center">
                {currentVersion.version_number}
              </TableCell>
              <TableCell align="center">
                {currentVersion.active_status}
              </TableCell>
              <TableCell align="center">{currentVersion.logloss}</TableCell>
              <TableCell align="center">{currentVersion.auc_roc}</TableCell>
              <TableCell align="center">{currentVersion.ks_score}</TableCell>
              <TableCell align="center">{currentVersion.gini_norm}</TableCell>
              <TableCell align="center">{currentVersion.rate_top10}</TableCell>
            </StyledTableRow>
          )}
        </TableBody>
      </Table>

      {/* {metricsArray(latestDrift).map((drift) => (
            <Metrics key={drift.title} metric={drift} />
          ))}
        </Grid> */}
      <Typography sx={{ fontWeight: "bold" }} variant="subtitle1">
        Approval Requests
      </Typography>
      <Stack spacing={4}>
        <Table size="median">
          <TableHead>
            <TableRow>
              <StyledTableCell sx={{ fontWeight: "bold" }}>
                Version
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Created At
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Requested by
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Description
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Status
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Log Loss
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                AUC ROC
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                KS Score
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Gini Norm
              </StyledTableCell>
              <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                Rate Top 10
              </StyledTableCell>
              {acceptedManagerialRoles.includes(role) && (
                <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                  Action
                </StyledTableCell>
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {requests &&
              requests.map((row) => (
                <StyledTableRow key={row.version_number}>
                  <TableCell align="center">{row.version_number}</TableCell>
                  <TableCell align="center">{row.created_time}</TableCell>
                  <TableCell align="center">{row.who_sumbit_request}</TableCell>
                  <TableCell align="center">
                    {row.submit_request_comment}
                  </TableCell>
                  <TableCell align="center">{row.request_status}</TableCell>

                  <TableCell align="center">{row.logloss}</TableCell>
                  <TableCell align="center">{row.auc_roc}</TableCell>
                  <TableCell align="center">{row.ks_score}</TableCell>
                  <TableCell align="center">{row.gini_norm}</TableCell>
                  <TableCell align="center">{row.rate_top10}</TableCell>
                  {acceptedManagerialRoles.includes(role) && (
                    <TableCell>
                      <LoadingButton
                        onClick={() =>
                          handleOpen(
                            row.version_number,
                            row.submit_request_comment
                          )
                        }
                      >
                        Review
                      </LoadingButton>
                    </TableCell>
                  )}
                </StyledTableRow>
              ))}
          </TableBody>
        </Table>
      </Stack>
    </React.Fragment>
  );
}

export default function Requests() {
  const reviewStatus = useSelector((state) => state?.project?.reviewStatus);
  const reviewError = useSelector((state) => state?.project?.reviewError);

  const dispatch = useDispatch();
  return (
    <Container sx={{ py: 4 }} maxWidth="xl">
      <Stack spacing={2}>
        <Typography variant="h6" align="left" sx={{ fontWeight: "bold" }}>
          Manage Pending Requests
        </Typography>
        {(reviewStatus === "success" || reviewStatus === "failed") && (
          <Alert
            key={"Alert"}
            sx={{ alignItems: "flex-start" }}
            variant="soft"
            color={reviewStatus === "success" ? "success" : "danger"}
            endDecorator={
              <IconButton
                onClick={() => dispatch(resetReview())}
                variant="soft"
                size="sm"
                color={reviewStatus === "success" ? "success" : "danger"}
              >
                <CloseRoundedIcon />
              </IconButton>
            }
          >
            <Typography fontWeight="lg" mt={0.25}>
              {reviewStatus === "success"
                ? "Review have successfully been submitted"
                : reviewError}
            </Typography>
          </Alert>
        )}
        <Paper
          sx={{
            p: 2,
            height: "100%",
          }}
          elevation={2}
        >
          <RequestTable />
        </Paper>
      </Stack>
    </Container>
  );
}
