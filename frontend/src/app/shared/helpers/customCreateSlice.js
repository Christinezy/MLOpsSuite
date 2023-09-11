import { createSlice } from "@reduxjs/toolkit";

const addLoadingCaseHelper = (builder, thunk, loadingKey, reducer) => {
  builder
    .addCase(thunk.pending, (draft) => {
      draft[loadingKey] = true;
    })
    .addCase(thunk.rejected, (draft) => {
      draft[loadingKey] = false;
    })
    .addCase(thunk.fulfilled, (draft, ...rest) => {
      draft[loadingKey] = false;
      reducer?.(draft, ...rest);
    });
  return {
    ...builder,
    addLoadingCase: (thunk, loadingKey, reducer) =>
      addLoadingCaseHelper(builder, thunk, loadingKey, reducer),
  };
};

export const customCreateSlice = (options) => {
  const { extraReducers } = options;
  if (typeof extraReducers !== "function") {
    return createSlice(options);
  }
  return createSlice({
    ...options,
    extraReducers: (builder) => {
      extraReducers({
        ...builder,
        addLoadingCase: (thunk, loadingKey, reducer) =>
          addLoadingCaseHelper(builder, thunk, loadingKey, reducer),
      });
    },
  });
};
