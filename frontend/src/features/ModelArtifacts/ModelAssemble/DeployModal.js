import * as React from "react";
import Button from "@mui/joy/Button";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import { Box } from "@mui/joy";
import { useDispatch, useSelector } from "react-redux";
import { deployModelThunk } from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);

export default function DeployModal(props) {
    const { inputs, open, handleClose, setAlertOpen } = props;
    const dispatch = useDispatch();

    const handleSubmit = (event) => {
    event.preventDefault();
    dispatch(
        deployModelThunk({
        id: projectId,
        payload: inputs,
        })
    ); 
    setAlertOpen(true);
    handleClose();
    };

    return (
        <React.Fragment>
            <Modal open={open} onClose={handleClose}>
                <ModalDialog
                sx={{ maxWidth: 400, width: "50%" }}
                >
                <ModalClose />
                <Box sx={{ mb: 3 }}>
                    <Typography component="h2" sx={{ fontWeight: "bold", mb: 2, fontSize: "18px" }}>
                    Confirm Deployment
                    </Typography>
                    <Typography sx={{ mb: 1, fontSize: "15px" }}>
                    Version: v{inputs.version}.0
                    </Typography>
                    <Typography sx={{ mb: 1, fontSize: "15px" }}>
                    Environment: {inputs.environment}
                    </Typography>
                    <Typography sx={{ mb: 1, fontSize: "15px" }}>
                    Strategy: {inputs.strategy}
                    </Typography>
                </Box>
                <Box component="form" onSubmit={handleSubmit} >
                <Stack justifyContent="center" spacing={2}>
                    <Button 
                        type="submit"
                    >
                        Deploy
                    </Button>
                </Stack>
                </Box>
                </ModalDialog>
            </Modal>
        </React.Fragment>
    );
  }