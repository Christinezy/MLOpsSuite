import { customCreateAsyncThunk } from "../../app/shared/helpers/customCreateAsyncThunk";
import { customCreateSlice } from "../../app/shared/helpers/customCreateSlice";
import {
    retrievePerformance,
    submitSelection,
    updateThreshold,
    getThreshold
} from "../api";

const PERFORMANCE_NAME = "performanceSlice";

export const initialState = {
    cpu_usage: 0,
    ram_usage: 0,
    num_containers: 0,
    timestamp: "",
    total_prediction: 0,
    total_requests: 0,

    cpu_usage_chart: [],
    ram_usage_chart: [],
    num_containers_chart: [],
    total_prediction_chart: [],
    total_requests_chart: [],

    error_message: "",
    success: "",

    threshold: 0,

    loadingPerformance: false
  };

export const retrievePerformanceThunk = customCreateAsyncThunk(
    `${PERFORMANCE_NAME}/RETRIEVE_PERFORMANCE`,
    (id) => {
      return retrievePerformance(id);
    }
);

export const submitSelectionThunk = customCreateAsyncThunk(
  `${PERFORMANCE_NAME}/SUBMIT_SELECTION`,
  ({ id, payload }) => {
    return submitSelection(id, payload);
  }
);

export const getThresholdThunk = customCreateAsyncThunk(
  `${PERFORMANCE_NAME}/GET_THRESHOLD`,
  (id) => {
    return getThreshold(id);
  }
);

export const updateThresholdThunk = customCreateAsyncThunk(
  `${PERFORMANCE_NAME}/UPDATE_THRESHOLD`,
  ({ id, payload }) => {
    return updateThreshold(id, payload);
  }
);

const performanceSlice = customCreateSlice({
    name: PERFORMANCE_NAME,
    initialState,
    extraReducers: (builders) => {
      builders
        .addLoadingCase(
          retrievePerformanceThunk,
          "loadingPerformance",
          (draft, action) => {
            const data = action.payload.data;
            if (data) {
              draft.cpu_usage = data.slice(-1)[0].cpu_usage;
              draft.ram_usage = data.slice(-1)[0].ram_usage;
              draft.num_containers = data.slice(-1)[0].num_containers;
              draft.timestamp = data.slice(-1)[0].timestamp;
              draft.total_prediction = data.slice(-1)[0].total_prediction;
              draft.total_requests = data.slice(-1)[0].total_requests;

              const getChart = (objs, property) => objs.map(
                (obj) => ({
                  time: obj.timestamp.slice(5,-4),
                  value: obj[property] 
                })
              );

              draft.total_prediction_chart = getChart(data, "total_prediction");
              draft.total_requests_chart = getChart(data, "total_requests")
              draft.num_containers_chart = getChart(data, "num_containers")
              draft.cpu_usage_chart = getChart(data, "cpu_usage")
              draft.ram_usage_chart = getChart(data, "ram_usage")
            }
          }
        )
        .addLoadingCase(
          submitSelectionThunk,
          "loadingSubmit",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.success = "Submit successfully.";
            }
            draft.error_message = action.payload.error_message;
          }
        )
        .addLoadingCase(
          getThresholdThunk,
          "loadingGetThreshold",
          (draft, action) => {
            draft.threshold = action.payload.cpu_threshold;
          }
        )
        .addLoadingCase(
          updateThresholdThunk,
          "loadingUpdateThreshold",
          (draft, action) => {
            draft.threshold = action.payload.updated_threshold;
          }
        )
    },
  });
  
  export const performanceSliceName = performanceSlice.name;
  export default performanceSlice.reducer;