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
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ArrowDropDownCircleSharpIcon from "@mui/icons-material/ArrowDropDownCircleSharp";
import ErrorRoundedIcon from "@mui/icons-material/ErrorRounded";

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
  "&:last-child td, &:last-child th": {
    border: 0,
  },
}));

function statusIcon(status) {
  const font = "16px";
  if (status === "Ok") {
    return <CheckCircleIcon sx={{ color: "#4caf50", fontSize: font }} />;
  } else if (status === "At Risk") {
    return (
      <ArrowDropDownCircleSharpIcon sx={{ color: "#FFBF00", fontSize: font }} />
    );
  } else if (status === "Failing") {
    return <ErrorRoundedIcon sx={{ color: "#ef5350", fontSize: font }} />;
  }
}

export function PredictionHealthInventory(props) {
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
              Performance
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Drift
            </StyledTableCell>
            <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
              Avg. Predictions/Day
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
              <TableCell align="center">
                {statusIcon(row.performance)}
              </TableCell>
              <TableCell align="center">{statusIcon(row.drift)}</TableCell>
              <TableCell align="center">{row.average_prediction}</TableCell>
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </React.Fragment>
  );
}
