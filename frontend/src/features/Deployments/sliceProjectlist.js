import { customCreateAsyncThunk } from "../../app/shared/helpers/customCreateAsyncThunk";
import { customCreateSlice } from "../../app/shared/helpers/customCreateSlice";
import {
    retrieveProjectlist,
    submitProjectCreation
} from "../api";

const PROJECTLIST_NAME = "projectlistSlice";

export const initialState = {
    projects: [],

    activeProjects: 0,
    performanceSummary: [0, 0, 0],
    driftSummary: [0, 0, 0],

    error_message: "",
    success: ""
  };

export const retrieveProjectlistThunk = customCreateAsyncThunk(
    `${PROJECTLIST_NAME}/RETRIEVE_LIST`,
    () => {
      return retrieveProjectlist();
    }
  );

export const submitProjectCreationThunk = customCreateAsyncThunk(
  `${PROJECTLIST_NAME}/CREATE_PROJECT`,
  (payload) => {
    return submitProjectCreation(payload);
  }
);

const projectlistSlice = customCreateSlice({
  name: PROJECTLIST_NAME,
  initialState,
  extraReducers: (builders) => {
    builders
      .addLoadingCase(
        retrieveProjectlistThunk,
        "loadingProjectlist",
        (draft, action) => {
          const data = action.payload.data;
          draft.projects = data;
          draft.activeProjects = data.filter((obj) => obj.status == "Live").length;

          draft.performanceSummary = [
            data.filter((obj) => obj.performance == "Ok").length,
            data.filter((obj) => obj.performance == "Warning").length,
            data.filter((obj) => obj.performance == "Error").length
          ]

          draft.driftSummary = [
            data.filter((obj) => obj.drift == "Ok").length,
            data.filter((obj) => obj.drift == "Warning").length,
            data.filter((obj) => obj.drift == "Error").length
          ]
        }
      )
      .addLoadingCase(
        submitProjectCreationThunk,
        "loadingProjectCreation",
        (draft, action) => {
          if (action.payload.status === "success") {
            draft.success = "Create project successfully.";
          }
          draft.error_message = action.payload.error_message;
        }
      )
  },
});
  
export const projectlistSliceName = projectlistSlice.name;
export default projectlistSlice.reducer;