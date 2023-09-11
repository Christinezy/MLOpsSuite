import * as React from "react";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { Stack } from "@mui/material";
import { useDispatch, useSelector } from "react-redux";
import { useState } from "react";
import ApprovalModal from "./ApprovalModal";
import DeployModal from "./DeployModal";
import { 
  updateApprovalThunk, 
  updateDeployThunk, 
  testVersionThunk, 
  updateTestThunk 
} from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);
const role = localStorage.getItem("role");

function GrayStatusBox(props) {
    return (
        <Box 
            sx={{ 
            border: "2px solid #e0e0e0", 
            borderRadius: 2,
            color: "#616161",
            width: "45%", 
            textAlign: "center",
            p: 1,
            mt: 3,
            }}
        >
        {props.text}
        </Box> 
    );
}

function GreenStatusBox(props) {
    return (
        <Box 
            sx={{ 
            border: "2px solid #4caf50", 
            borderRadius: 2,
            color: "#4caf50",
            width: "45%", 
            textAlign: "center",
            p: 1,
            mt: 3,
            }}
        >
        {props.text}
        </Box>
    );
}

function BlueStatusBox(props) {
  return (
      <Box 
          sx={{ 
          border: "2px solid #42a5f5", 
          borderRadius: 2,
          color: "#1976d2",
          width: "45%", 
          textAlign: "center",
          p: 1,
          mt: 3,
          }}
      >
      {props.text}
      </Box>
  );
}

function TestModel(props) {
  const {disabled, state, data} = props;
  const dispatch = useDispatch();
  const [alertOpen, setAlertOpen] = useState(false);

  const message = useSelector((state) => state.version.test_message);
  const status = useSelector((state) => state.version.test_status);

  const handleClick = () => {
    dispatch(testVersionThunk({
      id: projectId,
      payload: {
        version_number: state
      }
    }))
    setAlertOpen(true);
  };

  const handleCloseAlert = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }     
    setAlertOpen(false);
    if (status == "success") {
      dispatch(updateTestThunk({ state, data }))
    }  
  };

  return (
    <React.Fragment>
      {
        status == "success" &&
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={alertOpen}
          autoHideDuration={1000} 
          onClose={handleCloseAlert}
        >
          <Alert variant="filled" onClose={handleCloseAlert} severity="success" sx={{ width: '100%' }}>
            {message}
          </Alert>
        </Snackbar>
      }
      {
        status == "failed" &&
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={alertOpen} 
          autoHideDuration={3000} 
          onClose={handleCloseAlert}
        >
          <Alert variant="filled" onClose={handleCloseAlert}  severity="error" sx={{ width: '100%' }}>
            {message}
          </Alert>
        </Snackbar>
      }
      <Button color="primary" disabled={disabled} onClick={handleClick} sx={{ textTransform: "None" }}>
        Test Model
      </Button>
    </React.Fragment>

  );
}


function SendChangeRequest(props) {
  const {disabled, state, data} = props;
  const [modalOpen, setModalOpen] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);
  const dispatch = useDispatch();
  const message = useSelector((state) => state.version.submit_message);
  const status = useSelector((state) => state.version.submit_status);

  const handleClick = () => {
    setModalOpen(true);
  };

  const handleCloseAlert = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }     
    setAlertOpen(false);
    if (status == "success") {
      dispatch(updateApprovalThunk({ state, data })); 
    }  
  };
  return (
    <React.Fragment>
      {
        status == "success" &&
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={alertOpen}
          autoHideDuration={1000} 
          onClose={handleCloseAlert}
        >
          <Alert variant="filled" onClose={handleCloseAlert} severity="success" sx={{ width: '100%' }}>
            {message}
          </Alert>
        </Snackbar>
      }
      {
        status == "failed" &&
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={alertOpen} 
          autoHideDuration={3000} 
          onClose={handleCloseAlert}
        >
          <Alert variant="filled" onClose={handleCloseAlert}  severity="error" sx={{ width: '100%' }}>
            {message}
          </Alert>
        </Snackbar>
      }
      <ApprovalModal         
        open={modalOpen}
        state={state}
        handleClose={() => setModalOpen(false)}
        setAlertOpen={setAlertOpen}
      />
      <Button color="primary" disabled={disabled} onClick={handleClick} sx={{ textTransform: "None" }}>
        Submit Approval Request
      </Button>
    </React.Fragment>

  );
}

function DeployModel(props) {
    const {inputs, disabled, state, data } = props; 
    const [open, setOpen] = useState(false);
    const [alertOpen, setAlertOpen] = useState(false);
    const [missing, setMissing] = useState(false);
    const dispatch = useDispatch();

    const error_message = useSelector((state) => state.version.deploy_error_message);
    const success = useSelector((state) => state.version.deploy_success);
    

    const handleClick = (event) => {
      event.preventDefault();
      const missing_information = (!inputs.environment || !inputs.strategy)? true : false;
      if (missing_information) {
        setMissing(true);
      } else {
        setOpen(true);
      }
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
          dispatch(updateDeployThunk({ state, data }));
      }  
    };

    return (
      <React.Fragment>
        {
          success && !error_message &&
          <Snackbar 
            anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
            open={alertOpen}
            autoHideDuration={1000} 
            onClose={handleCloseAlert}
          >
            <Alert variant="filled" onClose={handleCloseAlert} severity="success" sx={{ width: '100%' }}>
              {success}
            </Alert>
          </Snackbar>
        }
        {
          error_message &&
          <Snackbar 
            anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
            open={alertOpen} 
            autoHideDuration={3000} 
            onClose={handleCloseAlert}
          >
            <Alert variant="filled" onClose={handleCloseAlert}  severity="error" sx={{ width: '100%' }}>
              {error_message}
            </Alert>
          </Snackbar>
        }
        <Snackbar 
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
          open={missing} 
          autoHideDuration={3000} 
          onClose={() => setMissing(false)}
        >
          <Alert variant="filled" onClose={() => setMissing(false)}  severity="error" sx={{ width: '100%' }}>
            Missing information.
          </Alert>
        </Snackbar>

        <DeployModal 
          inputs={inputs} 
          open={open} 
          handleClose={handleClose} 
          setAlertOpen={setAlertOpen}
        />
        <Button color="primary" disabled={disabled} onClick={handleClick} sx={{ textTransform: "None" }}>
          Deploy
        </Button>
      </React.Fragment>

    );
}


export default function Action(props) {
    const data = useSelector((state) => state.version.versions);
    const versionInfo = data.find(v => v.version_number === props.state);
    const approval_status = versionInfo.approval_status;
    const deploy_status = versionInfo.deploy_status;
    const test_status = versionInfo.test_status;

    return (
        <React.Fragment>
            <Typography variant="h7" sx={{ fontWeight: "bold" }} gutterBottom>
              Action
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
                <Stack 
                spacing={0}
                justifyContent="center"
                alignItems="center"
                >
                  {test_status == "test passed" && 
                    <React.Fragment>
                      <GreenStatusBox text="TEST PASSED" />
                      <TestModel 
                        disabled={true} 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>
                  }
                  {test_status == "testing" && 
                    <React.Fragment>
                      <BlueStatusBox text="TESTING" />
                      <TestModel 
                        disabled={true} 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>
                  }
                  {test_status == "not passed" && 
                    <React.Fragment>
                      <GrayStatusBox text="TEST NOT PASSED" />
                      <TestModel 
                        disabled={role != "MLOps Engineer" ? false : true} 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>
                  }

                  {approval_status == "approved" && 
                    <React.Fragment>
                      <GreenStatusBox text="APPROVED" />
                      <SendChangeRequest 
                        disabled={true} 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>
                  }
                  {approval_status == "pending approval" && 
                    <React.Fragment>
                      <BlueStatusBox text="PENDING APPROVAL" />
                      <SendChangeRequest 
                        disabled={true} 
                        state={props.state}  
                        data={data}
                      />
                    </React.Fragment>
                  }
                  {approval_status == "not approved" && 
                    <React.Fragment>
                      <GrayStatusBox text="NOT APPROVED" />
                        <SendChangeRequest 
                          disabled={
                            test_status == "test passed" && role != "MLOps Engineer" ?
                            false : true
                          } 
                          state={props.state} 
                          data={data}
                        />
                    </React.Fragment>
                  }

                  {deploy_status == "deployed" &&
                    <React.Fragment>
                      <GreenStatusBox text="DEPLOYED" />
                      <DeployModel 
                        inputs={props.inputs} 
                        disabled={true} 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>
                  }
                  {deploy_status == "deploying" && 
                    <React.Fragment>
                      <BlueStatusBox text="IN PROGRESS" />
                      <DeployModel 
                        inputs={props.inputs} 
                        disabled={true} 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>
                  }
                  {deploy_status == "not deployed" &&
                    <React.Fragment>
                      <GrayStatusBox text="NOT DEPLOYED" />
                      <DeployModel
                        inputs={props.inputs} 
                        disabled={
                          approval_status == "approved" && role != "Data Scientist" ? 
                          false : true
                        } 
                        state={props.state} 
                        data={data}
                      />
                    </React.Fragment>                     
                  }
                </Stack>
              </CardContent>
            </Card>
        </React.Fragment>
    );
}