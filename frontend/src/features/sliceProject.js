// Redux / Thunk Toolkits
import { useDispatch } from "react-redux";
import { customCreateAsyncThunk } from "../app/shared/helpers/customCreateAsyncThunk";
import { customCreateSlice } from "../app/shared/helpers/customCreateSlice";
import {
  retrieveProject,
  retrieveProjectRequests,
  retrieveProjectVersionOverview,
  submitReview,
} from "./api";

const PROJECT_NAME = "projectSlice";

export const initialState = {
  project_name: "",
  project_id: "",
  description: "",
  endpoint: "",
  status: "",
  deployment: "",
  build_environment: "",
  owner: "",
  approval_status: "",
  model_age: "",
  performance: "",
  drift: "",
  avg_prediction: "",
  versions: [],
  loadingReview: false,
  pendingApproval: false,
  loadingRequests: false,
  reviewStatus: "",
  reviewError: "",
  role: "",
  loadingRequests: false,
  date_created: "",
  min_num_nodes: 0,
  max_num_nodes: 0,
  desired_num_nodes: 0,
  loadingProject: false
};

export const retrieveProjectThunk = customCreateAsyncThunk(
  `${PROJECT_NAME}/RETRIEVE`,
  (id) => {
    return retrieveProject(id);
  }
);

export const retrieveVersionThunk = customCreateAsyncThunk(
  `${PROJECT_NAME}/RETRIEVE_VERSION`,
  (id) => {
    return retrieveProjectVersionOverview(id);
  }
);

export const submitReviewThunk = customCreateAsyncThunk(
  `${PROJECT_NAME}/SUBMIT_REVIEW`,
  async ({ id, payload }, { dispatch }) => {
    const response = submitReview(id, payload);
    await dispatch(retrieveVersionThunk(id));
    await dispatch(retrieveRequestsThunk(id));
    return response;
  }
);

export const retrieveRequestsThunk = customCreateAsyncThunk(
  `${PROJECT_NAME}/RETRIEVE_REQUESTS`,
  (id) => {
    return retrieveProjectRequests(id);
  }
);

const projectSlice = customCreateSlice({
  name: PROJECT_NAME,
  initialState,
  reducers: {
    resetReview: (draft) => {
      draft.reviewStatus = "";
      draft.reviewError = "";
    },
  },
  extraReducers: (builders) => {
    builders
      .addLoadingCase(
        retrieveProjectThunk,
        "loadingProject",
        (draft, action) => {
          draft.project_name = action.payload.project_name;
          draft.date_created = action.payload.date_created;
          draft.project_id = action.payload.project_id;
          draft.description = action.payload.description;
          draft.endpoint = action.payload.endpoint;
          draft.status = action.payload.status;
          draft.deployment = action.payload.deployment;
          draft.build_environment = action.payload.build_environment;
          draft.owner = action.payload.owner;
          draft.approval_status = action.payload.approval_status;
          draft.model_age = action.payload.model_age;
          draft.performance = action.payload.performance;
          draft.drift = action.payload.drift;
          draft.avg_prediction = action.payload.avg_prediction;
          draft.min_num_nodes = action.payload.min_num_nodes;
          draft.max_num_nodes = action.payload.max_num_nodes;
          draft.desired_num_nodes = action.payload.desired_num_nodes;
        }
      )
      .addLoadingCase(
        retrieveVersionThunk,
        "loadingVersion",
        (draft, action) => {
          draft.versions = action.payload.data;
          draft.pendingApproval = action.payload.pending_approval;
          draft.role = action.payload.role;
        }
      )
      .addLoadingCase(
        retrieveRequestsThunk,
        "loadingRequests",
        (draft, action) => {
          draft.requests = action.payload;
        }
      )
      .addLoadingCase(submitReviewThunk, "loadingReview", (draft, action) => {
        draft.reviewStatus = action.payload?.status;
        if (action.payload?.error_message) {
          draft.reviewError = action.payload?.error_message;
        }
      });
  },
});

export const projectSliceName = projectSlice.name;
export const { resetReview } = projectSlice.actions;
export default projectSlice.reducer;
