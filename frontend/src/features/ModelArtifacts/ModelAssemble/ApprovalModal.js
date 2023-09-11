import * as React from "react";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { Box, Textarea } from "@mui/joy";
import { useDispatch, useSelector } from "react-redux";
import { useState } from "react";
import { submitApprovalRequestThunk } from "../sliceVersion";

const projectId = window.location.href.substring(window.location.href.length - 1);

export default function ApprovalModal(props) {
  const { open, state, handleClose, setAlertOpen } = props; 
  const dispatch = useDispatch();

  const manager_email = useSelector((state) => state.version.manager_email);
  const manager_name = useSelector((state) => state.version.manager_name);
  const [manager, setManager] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    console.log(data.get("manager"));
    dispatch(
      submitApprovalRequestThunk({
      pid: projectId,
      vid: state,
      payload: {
        submit_request_comment: data.get("comment"),
        submit_to_who: data.get("manager")
      }
      })
    ); 
    setAlertOpen(true);
    handleClose();
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog
        sx={{ maxWidth: 600, width: "80%" }}
      >
        <ModalClose />
        <Typography id="basic-modal-dialog-title" component="h2">
          Submit Approval Request
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <Stack justifyContent="center" spacing={2}>
            <FormControl required>
              <FormLabel>Comment</FormLabel>
              <Textarea
                id="comment"
                name="comment"
                placeholder="Enter your comment here"
                required={true}
              />
            </FormControl>
            <FormControl required>
              <FormLabel>Select manager</FormLabel>
              <Select
                id="manager"
                name="manager"
                placeholder= "Select manager"
                value={manager}
                onChange={(e) => setManager(e.target.value)}
                sx={{ maxHeight: 40 }}
              >
                <MenuItem value={manager_email}>{manager_name + " (" + manager_email + ")"}</MenuItem>
              </Select>
            </FormControl>
            <Button type="submit">Submit</Button>
          </Stack>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
