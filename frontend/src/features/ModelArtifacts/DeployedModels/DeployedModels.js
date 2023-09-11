import * as React from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { Stack } from "@mui/material";
import { styled } from "@mui/material/styles";
import { tableCellClasses } from "@mui/material/TableCell";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import { useDispatch, useSelector } from "react-redux";
import Button from "@mui/material/Button";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import GoLiveModal from "./GoLiveModal";
import { updateGoLiveThunk } from "../sliceVersion";

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

const DEPLOYED_ACTIVE_STATUSES = new Set([
  "Active",
  "Test",
  "Canary",
  "Going Live",
]);

const role = localStorage.getItem("role");

function GoLive(props) {
  const { disabled, version, data } = props;
  const [open, setOpen] = React.useState(false);
  const [alertOpen, setAlertOpen] = React.useState(false);
  const dispatch = useDispatch();

  const error_message = useSelector(
    (state) => state.version.deploy_error_message
  );
  const success = useSelector((state) => state.version.deploy_success);

  const handleClick = (event) => {
    event.preventDefault();
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleCloseAlert = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setAlertOpen(false);
    if (success && !error_message) {
      const version_number = parseInt(version.version_number);
      dispatch(updateGoLiveThunk({ version_number, data }));
    }
  };

  return (
    <React.Fragment>
      {success && !error_message && (
        <Snackbar
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={alertOpen}
          autoHideDuration={1000}
          onClose={handleCloseAlert}
        >
          <Alert
            variant="filled"
            onClose={handleCloseAlert}
            severity="success"
            sx={{ width: "100%" }}
          >
            {success}
          </Alert>
        </Snackbar>
      )}
      {error_message && (
        <Snackbar
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={alertOpen}
          autoHideDuration={3000}
          onClose={handleCloseAlert}
        >
          <Alert
            variant="filled"
            onClose={handleCloseAlert}
            severity="error"
            sx={{ width: "100%" }}
          >
            {error_message}
          </Alert>
        </Snackbar>
      )}
      <GoLiveModal
        // inputs={inputs}
        version={version}
        open={open}
        handleClose={handleClose}
        setAlertOpen={setAlertOpen}
      />
      <Button
        color="primary"
        disabled={disabled}
        onClick={handleClick}
        sx={{ textTransform: "None" }}
      >
        Go Live
      </Button>
    </React.Fragment>
  );
}

function DeployedTable() {
  const data = useSelector((state) => state.version.versions);
  return (
    <React.Fragment>
      <Table size="median">
        <TableHead>
          <TableRow>
            <StyledTableCell sx={{ fontWeight: "bold" }}>
              Name & Description
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Created
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Deploy Status
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Version Status
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Test Status
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Traffic
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Action
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Remove
            </StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data
            ?.filter((row) => {
              return DEPLOYED_ACTIVE_STATUSES.has(row.active_status);
            })
            .map((row) => (
              <StyledTableRow key={row.version_number}>
                <TableCell>
                  <ListItem component="div" disablePadding>
                    <ListItemText
                      primary={"v" + row.version_number + ".0"}
                      secondary={row.version_description}
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
                <TableCell align="center">{row.created}</TableCell>
                <TableCell align="center">{row.deploy_status}</TableCell>
                <TableCell align="center">{row.active_status}</TableCell>
                <TableCell align="center">{row.deploy_test}/5</TableCell>
                <TableCell align="center">{row.traffic}%</TableCell>
                <TableCell align="center">
                  {" "}
                  {(() => {
                    if (row.active_status == "Test" && row.deploy_test >= 5) {
                      return (
                        <GoLive
                          disabled={role === "Manager"}
                          version={row}
                          data={data}
                        />
                      );
                    } else if (row.active_status == "Test") {
                      return (
                        <GoLive disabled={true} version={row} data={data} />
                      );
                    }
                  })()}
                </TableCell>
                <TableCell align="center">
                  {" "}
                  {(() => {
                    if (
                      row.active_status == "Test" ||
                      row.active_status == "Canary"
                    ) {
                      return "Remove";
                    }
                  })()}
                </TableCell>
              </StyledTableRow>
            ))}
        </TableBody>
      </Table>
    </React.Fragment>
  );
}

export default function DeployedModels() {
  return (
    <Container sx={{ py: 4 }} maxWidth="xl">
      <Stack spacing={2}>
        <Typography variant="h6" align="left" sx={{ fontWeight: "bold" }}>
          Deployed Models
        </Typography>
        <Paper
          sx={{
            p: 2,
            height: "100%",
          }}
          elevation={2}
        >
          <DeployedTable />
        </Paper>
      </Stack>
    </Container>
  );
}
