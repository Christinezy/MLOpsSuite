import { customCreateAsyncThunk } from "../../app/shared/helpers/customCreateAsyncThunk";
import { customCreateSlice } from "../../app/shared/helpers/customCreateSlice";
import {
    retrieveVersions,
    deployModel,
    goLiveModel,
    submitApprovalRequest,
    retrieveActiveVersion,
    retrieveManagerList,
    createVersion,
    codePortingRequest,
    getFile,
    saveFile,
    testVersion,
    getLintingComments
} from "../api";

const VERSION_NAME = "versionSlice";

export const initialState = {
    versions: [{
      "version_number": 1,
      "version_description": "",
      "created": "",
      "test_status": false,
      "approval_status": "not approved",
      "deploy_status": "not deployed",
      "active_status": false,
      "version_files": [{
        file_name: "",
        language_type: "",
      }]     
      }
    ],

    active_data: {
      "model_created_time": "",
      "deployment_environment": "",
      "deployment_strategy": "",
      "model_name": "",
      "version_number": 1,
    },
    active_status: false,


    deploy_error_message: "",
    deploy_success: "",

    submit_message: "",
    submit_status: "",

    manager_email: "",
    manager_name: "",

    create_status: "",
    create_message: "",

    porting_status: "",
    porting_message: "",

    getfile_status: "",
    getfile_message: "",
    getfile_code: "",

    savefile_status: "",
    savefile_message: "",

    test_status: "",
    test_message: "",

    linting_status: "",
    linting_message: "",

    loadingVersions: false,
    loadingActiveVersion: false,
    loadingManagerList: false
  };

export const createVersionThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/CREATE_VERSION`,
  ({id, payload}) => {
    return createVersion(id, payload);
  }
);

export const codePortingRequestThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/PORTING_REQUEST`,
  ({pid, vid, payload}) => {
    return codePortingRequest(pid, vid, payload);
  }
);

export const saveFileThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/SAVE_FILE`,
  ({pid, vid, payload}) => {
    return saveFile(pid, vid, payload);
  }
);

export const getFileThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/GET_FILE`,
  ({pid, vid, payload}) => {
    return getFile(pid, vid, payload);
  }
);

export const getLintingCommentsThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/GET_COMMENTS`,
  ({pid, vid, payload}) => {
    return getLintingComments(pid, vid, payload);
  }
);

export const resetLintingCommentsThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/RESET_COMMENTS`,
  () => {
    return "";
  }
);

export const updateTestThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/UPDATE_TEST`,
  ({state, data}) => {
    const versions = data.map(obj =>
      obj.version_number === state ? { ...obj, test_status: "testing" } : obj
  );
    return versions;
  }
);

export const updateApprovalThunk = customCreateAsyncThunk(
    `${VERSION_NAME}/UPDATE_APPROVAL`,
    ({state, data}) => {
      const versions = data.map(obj =>
        obj.version_number === state ? { ...obj, approval_status: "pending approval" } : obj
    );
      return versions;
    }
);

export const updateDeployThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/UPDATE_DEPLOY`,
  ({state, data}) => {
    const versions = data.map(obj =>
      obj.version_number === state ? { ...obj, deploy_status: "deploying" } : obj
  );
    return versions;
  }
);

export const updateGoLiveThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/UPDATE_GOLIVE`,
  ({version_number, data}) => {
    const versions = data.map(obj => {
      return (obj.version_number === version_number ? { ...obj, active_status: "Going Live" } : obj)
    }
  );
    return versions;
  }
);

export const retrieveVersionsThunk = customCreateAsyncThunk(
    `${VERSION_NAME}/RETRIEVE_VERSIONS`,
    (id) => {
      return retrieveVersions(id);
    }
);

export const retrieveActiveVersionThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/RETRIEVE_ACTIVE`,
  (id) => {
    return retrieveActiveVersion(id);
  }
);

export const retrieveManagerListThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/RETRIEVE_MANAGER`,
  (id) => {
    return retrieveManagerList(id);
  }
);

export const testVersionThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/TEST_VERSION`,
  ({id, payload}) => {
    return testVersion(id, payload);
  }
);

export const submitApprovalRequestThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/SUBMIT_APPROVAL`,
  ({pid, vid, payload}) => {
    return submitApprovalRequest(pid, vid, payload);
  }
);


export const deployModelThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/DEPLOY_MODEL`,
  ({id, payload}) => {
    return deployModel(id, payload);
  }
);

export const goLiveModelThunk = customCreateAsyncThunk(
  `${VERSION_NAME}/GOLIVE_MODEL`,
  ({id, payload}) => {
    return goLiveModel(id, payload);
  }
);

const versionSlice = customCreateSlice({
    name: VERSION_NAME,
    initialState,
    extraReducers: (builders) => {
      builders
        .addLoadingCase(
          retrieveVersionsThunk,
          "loadingVersions",
          (draft, action) => {
            if (action.payload.status != "failed") {
              draft.versions = action.payload.data;
            }
          }
        )
        .addLoadingCase(
          retrieveActiveVersionThunk,
          "loadingActiveVersion",
          (draft, action) => {
            draft.active_data = action.payload.data;
            draft.active_status = action.payload.active_status;
          }
        )
        .addLoadingCase(
          retrieveManagerListThunk,
          "loadingManagerList",
          (draft, action) => {
            draft.manager_email = action.payload.manager_email;
            draft.manager_name = action.payload.manager_name;
          }
        )
        .addLoadingCase(
          testVersionThunk,
          "loadingTestVersion",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.test_message = action.payload.message;
            } else{
              draft.test_message = action.payload.error_message;
            }
            draft.test_status = action.payload.status;         
          }
        )
        .addLoadingCase(
          deployModelThunk,
          "loadingDeploy",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.deploy_success = "Deployment message sent successfully.";
            }
            draft.deploy_error_message = action.payload.error_message;
          }
        )
        .addLoadingCase(
          goLiveModelThunk,
          "loadingGoLive",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.deploy_success = "Go live message sent successfully.";
            }
            draft.deploy_error_message = action.payload.error_message;
          }
        )
        .addLoadingCase(
          submitApprovalRequestThunk,
          "loadingSubmitApproval",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.submit_message = "Submit approval request successfully.";
            } else {
              draft.submit_message = action.payload.error_message;
            }    
            draft.submit_status = action.payload.status;
          }
        )
        .addLoadingCase(
          updateTestThunk,
          "loadingTest",
          (draft, action) => {
            draft.versions = action.payload;
          }
        )
        .addLoadingCase(
          updateApprovalThunk,
          "loadingUpdateApproval",
          (draft, action) => {
            draft.versions = action.payload;
          }
        )
        .addLoadingCase(
          updateDeployThunk,
          "loadingUpdateDeploy",
          (draft, action) => {
            draft.versions = action.payload;
          }
        )
        .addLoadingCase(
          updateGoLiveThunk,
          "loadingUpdateGoLive",
          (draft, action) => {
            draft.versions = action.payload;
          }
        )
        .addLoadingCase(
          createVersionThunk,
          "loadingCreateVersion",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.create_message = "Create new version successfully.";
            } else {
              draft.create_message = action.payload.error_message;
            }    
            draft.create_status = action.payload.status;
          }
        )
        .addLoadingCase(
          codePortingRequestThunk,
          "loadingPortingRequest",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.porting_message = "Submit code porting request successfully.";
            } else {
              draft.porting_message = action.payload.error_message;
            }    
            draft.porting_status = action.payload.status;
          }
        )
        .addLoadingCase(
          getFileThunk,
          "loadingGetFile",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.getfile_message = "Retrieve code successfully.";
              draft.getfile_code = action.payload.data;
            } else {
              draft.getfile_message = action.payload.error_message;
            }    
            draft.getfile_status = action.payload.status;
          }
        )
        .addLoadingCase(
          saveFileThunk,
          "loadingSaveFile",
          (draft, action) => {
            if (action.payload.status === "success") {
              draft.savefile_message = "Save code successfully.";
              draft.savefile_code = action.payload.data;
            } else {
              draft.savefile_message = action.payload.error_message;
            }    
            draft.savefile_status = action.payload.status;
          }
        )
        .addLoadingCase(
          getLintingCommentsThunk,
          "loadingGetComments",
          (draft, action) => {
              draft.linting_message = action.payload.error_message;
              draft.linting_status = action.payload.status;
            }         
        )
        .addLoadingCase(
          resetLintingCommentsThunk,
          "loadingResetComments",
          (draft, action) => {
              draft.linting_message = action.payload;
              draft.linting_status = action.payload;
            }         
        )
    },
  });
  
  export const versionSliceName = versionSlice.name;
  export default versionSlice.reducer;