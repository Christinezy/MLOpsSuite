import { configureStore } from "@reduxjs/toolkit";
import sessionSliceReducer from "../features/sliceSession";
import projectSliceReducer from "../features/sliceProject";
import projectlistSliceReducer from "../features/Deployments/sliceProjectlist";
import performanceSliceReducer from "../features/Performance/slicePerformance";
import versionSliceReducer from "../features/ModelArtifacts/sliceVersion";
import dataDriftSliceReducer from "../features/sliceDataDrift";

export const reducer = {
  session: sessionSliceReducer,
  project: projectSliceReducer,
  projectlist: projectlistSliceReducer,
  performance: performanceSliceReducer,
  version: versionSliceReducer,
  dataDrift: dataDriftSliceReducer,
};

export const store = configureStore({
  reducer,
});
