import * as React from "react";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import { Box, Textarea } from "@mui/joy";
import { useDispatch } from "react-redux";
import { createVersionThunk } from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);

export default function CreationModal(props) {
  const { open, handleClose, setAlertOpen } = props;
  const dispatch = useDispatch();
  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    dispatch(
      createVersionThunk({
        id: projectId,
        payload: {
          description: data.get("version_description"),
          githubFileURL: data.get("githubFileURL"),
        },
      })
    );
    setAlertOpen(true);
    handleClose();
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog
        sx={{ maxWidth: 800, width: "80%" }}
      >
        <ModalClose />
        <Typography id="basic-modal-dialog-title" component="h2">
          Create New Version
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <Stack justifyContent="center" spacing={2}>
            <FormControl>
              <FormLabel>Custom Version Description</FormLabel>
              <Textarea
                id="version_description"
                name="version_description"
                placeholder="Enter version description"
                required={true}
              />
            </FormControl>
            <FormControl>
              <FormLabel>GitHub URL</FormLabel>
              <Textarea
                id="githubFileURL"
                name="githubFileURL"
                placeholder="Enter GitHub URL of folder"
                required={true}
              />
            </FormControl>
            <Button type="submit">Create</Button>
          </Stack>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
