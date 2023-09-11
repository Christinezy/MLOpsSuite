import * as React from "react";
import Button from "@mui/joy/Button";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import { Box } from "@mui/joy";
import { useDispatch, useSelector } from "react-redux";
import { goLiveModelThunk } from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);

export default function GoLiveModal(props) {
    const { version, open, handleClose, setAlertOpen } = props;
    const dispatch = useDispatch();

    const handleSubmit = (event) => {
    event.preventDefault();
    dispatch(
        goLiveModelThunk({
        id: projectId,
        payload: {
            'version': version.version_number
        },
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
                    Confirm Go Live
                    </Typography>
                    <Typography sx={{ mb: 1, fontSize: "15px" }}>
                    Version: v{version.version_number}.0
                    </Typography>
                    <Typography sx={{ mb: 1, fontSize: "15px" }}>
                    Active Status: {version.active_status}
                    </Typography>
                    <Typography sx={{ mb: 1, fontSize: "15px" }}>
                    Test Status: {version.deploy_test} / 5
                    </Typography>
                </Box>
                <Box component="form" onSubmit={handleSubmit} >
                <Stack justifyContent="center" spacing={2}>
                    <Button 
                        type="submit"
                    >
                        Go Live
                    </Button>
                </Stack>
                </Box>
                </ModalDialog>
            </Modal>
        </React.Fragment>
    );
  }