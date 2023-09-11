import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Button from "@mui/material/Button";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import { useDispatch } from "react-redux";
import { logoutThunk } from "../../../features/sliceSession";
import { Avatar, MenuItem, Menu, Stack } from "@mui/joy";

function NavBarContent() {
  const dispatch = useDispatch();
  const [menuOpen, setMenuOpen] = React.useState(false);
  const name = localStorage.getItem("name");
  const role = localStorage.getItem("role");

  return (
    <AppBar
      position="static"
      color="default"
      elevation={0}
      sx={{ borderBottom: (theme) => `1px solid ${theme.palette.divider}` }}
    >
      <Toolbar sx={{ flexWrap: "wrap" }}>
        <Typography variant="h6" color="inherit" noWrap sx={{ flexGrow: 1 }}>
          Data Robot
        </Typography>

        <nav>
          <Link
            variant="button"
            color="text.primary"
            href="/deployments"
            sx={{ my: 1, mx: 1.5 }}
          >
            Deployments
          </Link>
          <Menu
            open={menuOpen}
            size="md"
            sx={{
              width: "180px",
              marginTop: "60px",
              marginLeft: "auto",
              right: "25px",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {role === "Admin" && (
              <MenuItem>
                <Button>
                  <Link
                    underline="none"
                    variant="button"
                    color="text.primary"
                    href="/settings"
                  >
                    Settings
                  </Link>
                </Button>
              </MenuItem>
            )}
            <MenuItem>
              <Button onClick={() => dispatch(logoutThunk())}>Logout</Button>
            </MenuItem>
          </Menu>
        </nav>
        <Button onClick={() => setMenuOpen(!menuOpen)}>
          <Stack sx={{ alignItems: "center" }} spacing={1} direction="row">
            <Avatar>{name[0]}</Avatar>
            <Typography color="text.primary" variant="overline">
              {name} | {role}
            </Typography>
          </Stack>
        </Button>
      </Toolbar>
    </AppBar>
  );
}

export default function NavBar() {
  return <NavBarContent />;
}
