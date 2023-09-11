import { createAsyncThunk } from "@reduxjs/toolkit";

export function customCreateAsyncThunk(typePrefix, payloadCreator, options) {
  const customPayloadCreator = async (arg, thunkAPI) => {
    try {
      // Pending: do some stuff before async call
      // Fulfilled: do some stuff after successful async call
      return await payloadCreator(arg, thunkAPI);
    } catch (err) {
      // Rejected: do some stuff after failed async call
      return thunkAPI.rejectWithValue(err);
    }
  };
  return createAsyncThunk(typePrefix, customPayloadCreator, options);
}
