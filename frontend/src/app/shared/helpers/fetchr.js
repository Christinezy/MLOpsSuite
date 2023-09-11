import { merge, cloneDeep } from "lodash";

const defaultOptions = {
  headers: {
    "Content-Type": "application/json",
  },
};

const getAccessToken = () => {
  return localStorage.getItem("jwt");
};

function checkStatus(response) {
  if (response.status === 204) {
    return Promise.resolve(null);
  }

  if (response.status >= 200 && response.status < 300) {
    return Promise.resolve(response);
  }

  return Promise.reject(response);
}

function generateQueryParamString(queryParams) {
  const resArr = [];
  queryParams.forEach((qp) => resArr.push(`${qp.key}=${qp.val}`));

  const res = resArr.join("&");
  return res ? `?${res}` : "";
}

const fetchr = async (
  endpoint,
  queryParams = [],
  _options = cloneDeep(defaultOptions),
  json = true
) => {
  const accessToken = getAccessToken();
  const options = { ..._options };
  options.headers.Authorization = `Bearer ${accessToken}`;
  //   options.headers.RequestID = v4();

  //   const apiDomain = getApiDomain();
  const apiDomain = "http://localhost:5050";

  return fetch(
    `${apiDomain}${endpoint}${generateQueryParamString(queryParams)}`,
    options
  );
  // .then(checkStatus)
  // .then((res) => {
  //   console.log(res);
  //   if (res) {
  //     return json ? res.json() : res.text();
  //   }
  //   return {};
  // });
};

export async function get(endpoint, queryParams = [], config = {}) {
  const options = merge(cloneDeep(defaultOptions), { ...config });
  options.method = "GET";

  return fetchr(endpoint, queryParams, options);
}

export async function post(endpoint, body = {}, config = {}) {
  const options = merge(cloneDeep(defaultOptions), { ...config });
  options.method = "POST";
  options.body = JSON.stringify(body);

  return fetchr(endpoint, [], options);
}

export async function put(endpoint, body = {}, config = {}) {
  const options = merge(cloneDeep(defaultOptions), { ...config });
  options.method = "PUT";
  options.body = JSON.stringify(body);

  return fetchr(endpoint, [], options);
}

export async function destroy(endpoint, config = {}) {
  const options = merge(cloneDeep(defaultOptions), { ...config });
  options.method = "DELETE";

  return fetchr(endpoint, [], options);
}
