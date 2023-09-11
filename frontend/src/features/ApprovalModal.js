import * as React from "react";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import { Box, Option, Select, Textarea } from "@mui/joy";
import { useDispatch, useSelector } from "react-redux";
import { submitReviewThunk } from "./sliceProject";
import { LoadingButton } from "@mui/lab";
import { TextField, MenuItem } from "@mui/material";

export default function ApprovalModal(props) {
  const { modelId, open, description, version, handleClose } = props;
  const dispatch = useDispatch();
  const loading = useSelector((state) => state?.project?.loadingRequests);
  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    dispatch(
      submitReviewThunk({
        id: modelId,
        payload: {
          version_number: version,
          handle_request_comment: data.get("handle_request_comment"),
          approval_result: data.get("approval_result"),
        },
      })
    );
    handleClose();
  };
  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog
        aria-labelledby="basic-modal-dialog-title"
        aria-describedby="basic-modal-dialog-description"
        sx={{ maxWidth: 800, width: "80%" }}
      >
        <ModalClose />
        <Typography id="basic-modal-dialog-title" component="h2">
          Submit review
        </Typography>

        <Typography
          id="basic-modal-dialog-description"
          textColor="text.tertiary"
        >
          Change description: {description}
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <Stack justifyContent="center" spacing={2}>
            <FormControl required>
              <FormLabel>Comments</FormLabel>
              <Textarea
                id="handle_request_comment"
                name="handle_request_comment"
                placeholder="Add comments for review"
              />
            </FormControl>
            <FormLabel>Approve/Reject</FormLabel>
            <TextField
              id="approval_result"
              name="approval_result"
              placeholder="Select a review decision"
              select
              size="small"
              required
            >
              <MenuItem value={true}>Approve</MenuItem>
              <MenuItem value={false}>Reject</MenuItem>
            </TextField>
            <LoadingButton loading={loading} type="submit">
              Submit review
            </LoadingButton>
          </Stack>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
