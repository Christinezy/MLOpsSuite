// Redux / Thunk Toolkits
import { customCreateAsyncThunk } from "../app/shared/helpers/customCreateAsyncThunk";
import { customCreateSlice } from "../app/shared/helpers/customCreateSlice";
import { retrieveDataDrift } from "./api";

const DATA_DRIFT_NAME = "dataDriftSlice";

export const selectDataDrift = (state) => state.dataDrift.driftArray;
export const selectDataDriftLatest = (state) => state.dataDrift.latestDrift;
export const selectDataDriftLoading = (state) =>
  state.dataDrift.loadingDataDrift;

export const initialState = {
  driftArray: [],
  latestDrift: {},
  loadingDataDrift: false,
};

export const retrieveDataDriftThunk = customCreateAsyncThunk(
  `${DATA_DRIFT_NAME}/RETRIEVE`,
  (id) => {
    return retrieveDataDrift(id);
  }
);

const dataDriftSlice = customCreateSlice({
  name: DATA_DRIFT_NAME,
  initialState,
  extraReducers: (builders) => {
    builders.addLoadingCase(
      retrieveDataDriftThunk,
      "loadingDataDrift",
      (draft, action) => {
        draft.driftArray = action.payload.data;
        draft.latestDrift = action.payload.data[action.payload.data.length - 1];
      }
    );
  },
});

export const dataDriftSliceName = dataDriftSlice.name;
export default dataDriftSlice.reducer;
