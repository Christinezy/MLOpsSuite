import * as React from "react";
import Button from "@mui/joy/Button";
import FormControl from "@mui/joy/FormControl";
import FormLabel from "@mui/joy/FormLabel";
import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";
import Stack from "@mui/joy/Stack";
import Typography from "@mui/joy/Typography";
import ModalClose from "@mui/joy/ModalClose";
import { Box, Option, Select, Textarea } from "@mui/joy";
import { useDispatch } from "react-redux";
import { submitProjectCreationThunk } from "./sliceProjectlist";

export default function ProjectCreationModal(props) {
  const { open, handleClose } = props;
  const dispatch = useDispatch();
  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    dispatch(
      submitProjectCreationThunk({
            projectName: data.get("projectName"),
            projectGithubId: data.get("projectGithubId"),
            githubProjectName: data.get("githubProjectName"),
            fileLoc: data.get("fileLoc"),
            get_code_type: data.get("get_code_type"),
            mlModelName: data.get("mlModelName")
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
          Create New Project
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <Stack justifyContent="center" spacing={2}>
            <FormControl>
              <FormLabel>Desired Project Name</FormLabel>
              <Textarea
                id="projectName"
                name="projectName"
                placeholder="Enter your Desired Project Name"
              />
            </FormControl>
            <FormControl>
              <FormLabel>GitHub ID</FormLabel>
              <Textarea
                id="projectGithubId"
                name="projectGithubId"
                placeholder="Enter owner's GitHub ID"
              />
            </FormControl>
            <FormControl>
              <FormLabel>GitHub Project Name</FormLabel>
              <Textarea
                id="githubProjectName"
                name="githubProjectName"
                placeholder="Enter GitHub Project Name"
              />
            </FormControl>
            <FormControl>
              <FormLabel>File Path to Model</FormLabel>
              <Textarea
                id="fileLoc"
                name="fileLoc"
                placeholder="Enter file path to model"
              />
            </FormControl>
            <FormControl>
              <FormLabel>File Type</FormLabel>
              <Select
                id="get_code_type"
                name="get_code_type"
                placeholder="Select file type"
                required
              >
                <Option value="file">File</Option>
                <Option value="model">Model</Option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Custom Model Name</FormLabel>
              <Textarea
                id="mlModelName"
                name="mlModelName"
                placeholder="Enter a custom Model name"
              />
            </FormControl>
            <FormControl>
              <FormLabel>Custom Model Description</FormLabel>
              <Textarea
                id="mlModelDescription"
                name="mlModelDescription"
                placeholder="Enter a custom Model description"
              />
            </FormControl>
            <Button type="submit">Create</Button>
          </Stack>
        </Box>
      </ModalDialog>
    </Modal>
  );
}
