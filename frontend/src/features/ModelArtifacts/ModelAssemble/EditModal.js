import * as React from "react";
import Button from "@mui/joy/Button";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { Box } from "@mui/joy";
import { useDispatch, useSelector } from "react-redux";
import { useState } from "react";
import MonacoEditor from "react-monaco-editor";
import Grid from "@mui/material/Grid";
import { 
  getLintingCommentsThunk, 
  resetLintingCommentsThunk,
  saveFileThunk,
} from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);

function LintingForm(props) {
  const [code, setCode] = useState(props.code);
  const status = useSelector((state) => state.version.linting_status);
  const error_message = useSelector((state) => state.version.linting_message);

  const handleEditorChange = (newValue) => {
    setCode(newValue);
    const base64_code = window.btoa(newValue);
    props.setFilecode(base64_code);
    props.setEdited(true);
  };

  return (
    <React.Fragment>
      <div style={{ display: 'flex' }}>     
        <MonacoEditor
          width={status? "65%" : "100%"}
          height="580"
          language='python'
          theme="vs"
          value={code}
          onChange={handleEditorChange}
        />
        {status && (
          <Box 
              component="main"
              sx={{
                  flexGrow: 1,
                  height: "580px",
                  overflow: "auto",
                  width:"35%",
                  ml: "20px"
              }}
          >
            <h2>
              {status=="success"? 
                "Linting Comments" : "Failed to get linting comments"
              }
            </h2>
            <Typography 
              gutterBottom
              sx={{ whiteSpace: "pre-wrap", fontSize: "14px", color: "black", lineHeight: 2}}
            >
                {error_message}
            </Typography>
          </Box>
        )}
      </div>
    </React.Fragment>
  );
}


export default function EditModal(props) {
  const { file_name, open, setOpen, state } = props;
  const [edited, setEdited] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);
  
  const dispatch = useDispatch();
  const getfile_code = useSelector((state) => state.version.getfile_code);
  const [filecode, setFilecode] = useState(getfile_code);
  const code = window.atob(getfile_code);

  const message = useSelector((state) => state.version.savefile_message);
  const status = useSelector((state) => state.version.savefile_status);

  const handleClose = (event) => {
    setOpen(false);
    setEdited(false);
    dispatch(resetLintingCommentsThunk());
  }

  const handleClick = (event) => {
    event.preventDefault();
    dispatch(
      getLintingCommentsThunk({
        pid: projectId,
        vid: state,
        payload: {
          filename: file_name
        }
      })
    );
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    setEdited(false);
    setAlertOpen(true);
    dispatch(saveFileThunk({
      pid: projectId,
      vid: state,
      payload: {
        filename: file_name,
        file: filecode
      }
    }));
  };

  const handleCloseAlert = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }     
    setAlertOpen(false);
  };

  return (
    <React.Fragment>
      {
        status == "success" &&
        <Snackbar 
          anchorOrigin={{ vertical: "top", horizontal: "center" }}
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
          anchorOrigin={{ vertical: "top", horizontal: "center" }}
          open={alertOpen} 
          autoHideDuration={3000} 
          onClose={handleCloseAlert}
        >
          <Alert variant="filled" onClose={handleCloseAlert}  severity="error" sx={{ width: '100%' }}>
            {message}
          </Alert>
        </Snackbar>
      }
      <Modal open={open} onClose={handleClose}>
        <ModalDialog
          aria-labelledby="basic-modal-dialog-title"
          aria-describedby="basic-modal-dialog-description"
          sx={{ maxWidth: "100%", width: "85%", height: 800 }}
        >
          <ModalClose />
          <Typography id="basic-modal-dialog-title" component="h2">
            {file_name}
          </Typography>
          <Box component="form" onSubmit={handleSubmit}>
            <Stack justifyContent="center" spacing={2}>
              <LintingForm 
                code={code} 
                setEdited={setEdited}
                setFilecode={setFilecode}
              />
              <Grid container spacing={2} justifyContent="center">
                <Grid item xs={2.5}>
                  <Button 
                    fullWidth
                    onClick={handleClick}
                    disabled={edited}
                  >
                    Get Linting Comments
                  </Button>
                </Grid>
                <Grid item xs={2.5}>
                  <Button 
                    type="submit" 
                    fullWidth
                    disabled={!edited}
                  >
                    Save
                  </Button>
                </Grid>
              </Grid>
            </Stack>
          </Box>
        </ModalDialog>
      </Modal>
    </React.Fragment>
  );
}
