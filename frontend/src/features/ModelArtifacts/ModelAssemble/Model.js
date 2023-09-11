import * as React from "react";
import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { List } from "@mui/material";
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Divider from '@mui/material/Divider';
import AddIcon from '@mui/icons-material/Add';
import DescriptionIcon from '@mui/icons-material/Description';
import EditIcon from '@mui/icons-material/Edit';
import CreationModal from "./CreationModal";
import IconButton from '@mui/material/IconButton';
import EditModal from "./EditModal";
import LoopIcon from '@mui/icons-material/Loop';
import CircularProgress from '@mui/material/CircularProgress';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { useDispatch } from "react-redux";
import { retrieveVersionsThunk, getFileThunk } from "../sliceVersion";
import CodePortingModal from "./CodePortingModal";

const projectId = window.location.href.substring(window.location.href.length - 1);
const role = localStorage.getItem("role");

function SelectVersion(props) {
  const { handleDeployInputs, selectState, versionNums, setEnv, setStrategy } = props;
  const [version, setVersion] = React.useState(1);
  const handleChange = (event) => {
    setVersion(event.target.value);
    handleDeployInputs("version", parseInt(event.target.value));
    handleDeployInputs("environment", "");
    handleDeployInputs("strategy", "");
    setEnv("");
    setStrategy("");
    selectState(event.target.value);
  };

  return (
    <FormControl sx={{ m: 1, minWidth: "100%" }} size="small">
      <Select
        value={version}
        onChange={handleChange}
      >
        {
          versionNums.map((num) => (
            <MenuItem value={num}>
              {"v" + num.toString() + ".0"}
            </MenuItem>
          ))
        }
      </Select>
    </FormControl>
  );
}

function FileList(props) {
  const [open, setOpen] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [porting, setPorting] = useState(false);
  const [file, setFile] = useState("");
  const [lang, setLang] = useState("");
  
  const dispatch = useDispatch();
  const versionInfo = props.versionInfo;
  const files = versionInfo.version_files;
  const approval_status = versionInfo.approval_status;
  const disabled = (
    approval_status == "not approved" && !isLoading
    ) ? false : true;

  const message = useSelector((state) => state.version.porting_message);
  const status = useSelector((state) => state.version.porting_status);

  const handleClick = (event) => {
    setFile(event.currentTarget.value);
    dispatch(getFileThunk({
      pid: projectId,
      vid: props.state,
      payload: {
        filename: event.currentTarget.value
      }
    }))
    setTimeout(() => setOpen(true), 800);  
  }

  const handleClickPorting = (event) => {
    setFile(event.currentTarget.value);
    setLang(files.find(f => f.file_name == event.currentTarget.value).language_type)
    setPorting(true);
  }

  const handleCloseAlert = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }     
    setAlertOpen(false);
    if (status == "success") {
      setIsLoading(true);
      setTimeout(() => setIsLoading(false), 40000);  
      setTimeout(() => dispatch(retrieveVersionsThunk(projectId)), 40000);       
    }  
  };

  return (
    <React.Fragment>
      <Box sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",    
      }}>
        {isLoading && <CircularProgress size={25} />}
      </Box>

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
          autoHideDuration={2000} 
          onClose={handleCloseAlert}
        >
          <Alert variant="filled" onClose={handleCloseAlert}  severity="error" sx={{ width: '100%' }}>
            {message}
          </Alert>
        </Snackbar>
      }
      <CodePortingModal 
        file_name={file}
        language_type={lang}
        state={props.state}
        open={porting}
        handleClose={() => setPorting(false)}   
        setAlertOpen={setAlertOpen}   
      />
      <EditModal 
        file_name={file}
        open={open}
        setOpen={setOpen}
        state={props.state}
      />
      <List>
        {
          files.map((file) => (
            <React.Fragment>
              <ListItem 
                key={file.file_name}
                secondaryAction={
                  <React.Fragment>
                    {
                      file.language_type == "" || role == "MLOps Engineer"?
                      <em></em>
                      :
                      <IconButton 
                        edge="end" 
                        value={file.file_name}
                        disabled={disabled}
                        onClick={handleClickPorting}
                      >
                        <LoopIcon             
                          sx={{ fontSize: "16px", mx: 1 }}
                        />
                      </IconButton>
                    }
                    {
                      file.language_type == "" || role == "MLOps Engineer"?
                      <em></em>
                      :
                      <IconButton 
                        edge="end" 
                        value={file.file_name}
                        disabled={disabled}
                        onClick={handleClick}
                      >
                        <EditIcon             
                          sx={{ fontSize: "15px", mx: 1 }}
                        />
                      </IconButton>
                    }
                  </React.Fragment>
                }          
                component="div" 
                disablePadding
              >
                <ListItemIcon>
                  <DescriptionIcon sx={{ fontSize: 15 }} />
                </ListItemIcon>
                <ListItemText
                  primary={file.file_name}
                  primaryTypographyProps={{
                    fontSize: 14,
                    fontWeight: "medium",
                    ml: -3,
                  }}
                />       
              </ListItem>   
              <Divider />
            </React.Fragment>
          ))
        }
      </List>
    </React.Fragment>
  );
}

export default function Model(props) {
    const [modalOpen, setModalOpen] = useState(false);
    const [alertOpen, setAlertOpen] = useState(false);
    const dispatch = useDispatch();

    const data = useSelector((state) => state.version.versions);
    const versionInfo = data.find(v => v.version_number === props.state);
    const versionNums = (data.map(v => v.version_number)).sort();

    const message = useSelector((state) => state.version.create_message);
    const status = useSelector((state) => state.version.create_status);

    const handleCloseAlert = (event, reason) => {
      if (reason === "clickaway") {
        return;
      }     
      setAlertOpen(false);
      if (status == "success") {
        dispatch(retrieveVersionsThunk(projectId));
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
            <CreationModal         
                open={modalOpen}
                handleClose={() => setModalOpen(false)}
                setAlertOpen={setAlertOpen}
            />
            <Typography variant="h7" sx={{ fontWeight: "bold" }} gutterBottom>
              Model
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
                    Versions
                  </Typography>
                  {role != "MLOps Engineer" &&
                    <Button 
                      color="primary" 
                      startIcon={<AddIcon />} 
                      onClick={() => setModalOpen(true)}>
                        New version
                    </Button>
                  }
                </Box>
                <SelectVersion 
                  handleDeployInputs={props.handleDeployInputs} 
                  versionNums={versionNums}
                  selectState={props.selectState}
                  setEnv={props.setEnv}
                  setStrategy={props.setStrategy}
                />
                <Typography variant="subtitle2" color="gray" sx={{ mb: 3 }}>
                  {versionInfo.version_description}
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: "bold" }}>
                  Content
                </Typography>
                <FileList 
                  versionInfo={versionInfo} 
                  state={props.state}
                />
              </CardContent>
            </Card>
        </React.Fragment>
    );
}