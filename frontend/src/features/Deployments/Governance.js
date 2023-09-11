import * as React from "react";
import Link from "@mui/material/Link";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import { styled } from "@mui/material/styles";
import { tableCellClasses } from "@mui/material/TableCell";

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    color: theme.palette.common.black,
    fontSize: 14,
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  "&:nth-of-type(odd)": {
    backgroundColor: theme.palette.action.hover,
  },
  // hide last border
  "&:last-child td, &:last-child th": {
    border: 0,
  },
}));

export function GovernanceInventory(props) {
  const data = props.data;
  return (
    <React.Fragment>
      <Table size="median">
        <TableHead>
          <TableRow>
            <StyledTableCell sx={{ fontWeight: "bold" }}>
              Project Name
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Status
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Build Env.
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Deployment
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Owners
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Model Age
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Approval Status
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Endpoint
            </StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => (
            <StyledTableRow key={row.id}>
              <TableCell>
                <Link
                  href={"/deployments/" + row.project_id.toString()}
                  underline="none"
                  color="inherit"
                >
                  <ListItem component="div" disablePadding>
                    <ListItemText 
                        primary={row.project_name} 
                        secondary={row.description} 
                        primaryTypographyProps={{
                            fontSize: 14,
                            fontWeight: "bold",
                            mt: -1,
                        }}
                        secondaryTypographyProps={{
                            fontSize: 13,
                            mb: -1,
                        }}
                    />
                    </ListItem>
                </Link>
              </TableCell>
              <TableCell align="center">{row.status}</TableCell>
              <TableCell align="center">{row.build_environment}</TableCell>
              <TableCell align="center">{row.deployment}</TableCell>
              <TableCell align="center">{row.owner}</TableCell>
              <TableCell align="center">{row.model_age + " days"}</TableCell>
              <TableCell align="center">{row.approval_status}</TableCell>
              <TableCell align="center">{row.endpoint}</TableCell>
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </React.Fragment>
  );
}
