import * as React from "react";
import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { Alert, MenuItem } from "@mui/material";
import { useSelector, useDispatch } from "react-redux";
import { selectCreateSuccess, selectSessionError } from "./sessionSelectors";
import { createUserThunk } from "./sliceSession";

const theme = createTheme();

export default function AdminSettings() {
  const dispatch = useDispatch();
  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    dispatch(
      createUserThunk({
        email: data.get("email"),
        password: data.get("password"),
        firstname: data.get("firstname"),
        lastname: data.get("lastname"),
        role: data.get("role"),
        github_id: data.get("github_id"),
        github_credentials: data.get("github_credentials"),
      })
    );
  };

  const sessionError = useSelector(selectSessionError);
  const success = useSelector(selectCreateSuccess);
  return (
    <ThemeProvider theme={theme}>
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: "secondary.main" }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Create Account
          </Typography>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                {sessionError && <Alert severity="error">{sessionError}</Alert>}
                {success && !sessionError && (
                  <Alert severity="success">{success}</Alert>
                )}
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  autoComplete="given-name"
                  name="firstname"
                  required
                  fullWidth
                  id="firstname"
                  label="First Name"
                  autoFocus
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  id="lastname"
                  label="Last Name"
                  name="lastname"
                  autoComplete="family-name"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  select
                  fullWidth
                  id="role"
                  name="role"
                  label="Role"
                  autoComplete="role"
                  defaultValue=""
                >
                  <MenuItem value={0}>Admin</MenuItem>
                  <MenuItem value={1}>Data Scientist</MenuItem>
                  <MenuItem value={2}>Manager</MenuItem>
                  <MenuItem value={3}>MLOps Engineer</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="github_id"
                  label="Github ID"
                  name="github_id"
                  autoComplete="github_id"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="github_credentials"
                  label="Github Credentials"
                  name="github_credentials"
                  autoComplete="github_credentials"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                />
              </Grid>
            </Grid>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Create account
            </Button>
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
