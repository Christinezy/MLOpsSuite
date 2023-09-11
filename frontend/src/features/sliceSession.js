// Redux / Thunk Toolkits
import { customCreateAsyncThunk } from "../app/shared/helpers/customCreateAsyncThunk";
import { customCreateSlice } from "../app/shared/helpers/customCreateSlice";
import {
  login as loginAPI,
  createUser as createUserAPI,
  logout as logoutAPI,
} from "./api";

const SESSION_NAME = "sessionSlice";

export const initialState = {
  name: "",
  error_message: "",
  loadingLogin: false,
  loadingCreate: false,
  create_success: "",
  role: "",
};

export const loginThunk = customCreateAsyncThunk(
  `${SESSION_NAME}/LOGIN`,
  (payload) => {
    console.log("here");
    return loginAPI(payload);
  }
);

export const createUserThunk = customCreateAsyncThunk(
  `${SESSION_NAME}/CREATE_USER`,
  (payload) => {
    return createUserAPI(payload);
  }
);

export const logoutThunk = customCreateAsyncThunk(
  `${SESSION_NAME}/LOGOUT`,
  logoutAPI
);

const sessionSlice = customCreateSlice({
  name: SESSION_NAME,
  initialState,
  extraReducers: (builders) => {
    builders
      .addLoadingCase(loginThunk, "loadingLogin", (draft, action) => {
        draft.error_message = action.payload.error_message;
        if (action.payload.status === "success") {
          localStorage.setItem("name", action.payload.name);
          localStorage.setItem("role", action.payload.role);
          localStorage.setItem("jwt", action.payload.token);
          window.location.href = "/deployments";
        }
      })
      .addLoadingCase(createUserThunk, "loadingCreate", (draft, action) => {
        if (action.payload.status === "success") {
          draft.create_success = "User created successfully!";
        }
        draft.error_message = action.payload.error_message;
      })
      .addLoadingCase(logoutThunk, "loadingLogout", (draft) => {
        localStorage.removeItem("jwt");
        localStorage.removeItem("name");
        localStorage.removeItem("role");
        window.location.href = "/login";
        draft.name = "";
      });
  },
});

export const sessionSliceName = sessionSlice.name;
export const { login } = sessionSlice.actions;
export default sessionSlice.reducer;
