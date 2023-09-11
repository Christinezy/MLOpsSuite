import { get, post } from "../app/shared/helpers/fetchr";

export const login = async (payload) => {
  const requestOptions = {
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: payload.email,
      password: payload.password,
    }),
    method: "POST",
  };
  const response = await fetch("http://localhost:5050/login", requestOptions);
  const data = await response.json();
  return data;
};

export const logout = async () => {
  return get("/logout");
};

export const createUser = async (payload) => {
  const requestOptions = {
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: payload.email,
      password: payload.password,
      firstname: payload.firstname,
      lastname: payload.lastname,
      role: payload.role,
      github_id: payload.github_id,
      github_credentials: payload.github_credentials,
    }),
    method: "POST",
  };
  const response = await fetch(
    "http://localhost:5050/admin/create_user",
    requestOptions
  );
  const data = await response.json();
  return data;
};

export const retrieveProject = async (id) => {
  const response = await get(`/project/${id}/overview`);
  const data = await response.json();
  return data;
};

export const retrieveProjectVersionOverview = async (id) => {
  const response = await get(
    `/project/${id}/model/governance/versions/overview`
  );
  const data = await response.json();
  return data;
};

export const submitReview = async (id, payload) => {
  const response = await post(
    `/project/${id}/model/requests/handle_approval_request`,
    payload
  );
  const data = await response.json();
  return data;
};

export const retrieveProjectlist = async () => {
  const response = await get("/list-projects");
  const data = await response.json();
  return data;
};

export const retrievePerformance = async (id) => {
  const response = await get(`/project/${id}/performance`);
  const data = await response.json();
  return data;
};

export const deployModel = async (id, payload) => {
  const response = await post(`/project/${id}/create-deployment`, payload);
  const data = await response.json();
  return data;
};

export const goLiveModel = async (id, payload) => {
  const response = await post(`/project/${id}/go-live`, payload);
  const data = await response.json();
  return data;
};

export const submitSelection = async (id, payload) => {
  const response = await post(`/project/${id}/update-hpa`, payload);
  const data = await response.json();
  return data;
};

export const submitProjectCreation = async (payload) => {
  const response = await post("/admin/get_file", payload);
  const data = await response.json();
  return data;
};

export const retrieveVersions = async (id) => {
  const response = await get(`/project/${id}/model/versions/list_versions`);
  const data = await response.json();
  return data;
};

export const retrieveActiveVersion = async (id) => {
  const response = await get(`/project/${id}/model/active_version/overview`);
  const data = await response.json();
  return data;
};

export const retrieveDataDrift = async (id) => {
  const response = await get(`/project/${id}/data-drift`);
  const data = await response.json();
  return data;
};

export const submitApprovalRequest = async (pid, vid, payload) => {
  const response = await post(
    `/project/${pid}/model/versions/${vid}/submit_approval_request`,
    payload
  );
  const data = await response.json();
  return data;
};

export const retrieveProjectRequests = async (id) => {
  const response = await get(`/project/${id}/requests/list_requests`);
  const data = await response.json();
  return data;
};
export const retrieveManagerList = async (id) => {
  const response = await get(`/list-project-manager/${id}`);
  const data = await response.json();
  return data;
};

export const createVersion = async (id, payload) => {
  const response = await post(`/project/${id}/model/create_version`, payload);
  const data = await response.json();
  return data;
};

export const getThreshold = async (id) => {
  const response = await get(`/get-project-threshold/${id}`);
  const data = await response.json();
  return data;
};

export const updateThreshold = async (id, payload) => {
  const response = await get(`/update-project-threshold/${id}/${payload}`);
  const data = await response.json();
  return data;
};

export const codePortingRequest = async (pid, vid, payload) => {
  const response = await post(
    `/project/${pid}/model/versions/${vid}/code-port`,
    payload
  );
  const data = await response.json();
  return data;
};

export const getFile = async (pid, vid, payload) => {
  const response = await post(
    `/project/${pid}/model/versions/${vid}/get-file`,
    payload
  );
  const data = await response.json();
  return data;
};

export const testVersion = async (id, payload) => {
  const response = await post(
    `/project/${id}/model/versions/test`,
    payload
  );
  const data = await response.json();
  return data;
};

export const getLintingComments = async (pid, vid, payload) => {
  const response = await post(
    `/project/${pid}/model/versions/${vid}/lint-comments`,
    payload
  );
  const data = await response.json();
  return data;
};

export const saveFile = async (pid, vid, payload) => {
  const response = await post(
    `/project/${pid}/model/versions/${vid}/save-file`,
    payload
  );
  const data = await response.json();
  return data;
};
