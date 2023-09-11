import * as React from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { Stack } from "@mui/material";
import { styled } from "@mui/material/styles";
import { tableCellClasses } from "@mui/material/TableCell";
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Paper from "@mui/material/Paper";
import { useSelector } from "react-redux";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import IconButton from '@mui/material/IconButton';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';


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

const StyledCollapsibleRow = styled(TableRow)(({ theme }) => ({
    "&:last-child td, &:last-child th": {
        border: 0,
    },
}));

function Row(props) {
    const { row } = props;
    const [open, setOpen] = React.useState(false);

    return (
        <React.Fragment>
            <StyledTableRow key={row.version_number}>
                <TableCell>
                <IconButton
                    aria-label="expand row"
                    size="small"
                    onClick={() => setOpen(!open)}
                >
                    {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                </IconButton>
                </TableCell>
                <TableCell sx={{maxWidth: "500px"}}>
                    <ListItem component="div" disablePadding>
                        <ListItemText 
                            primary={"v" + row.version_number + ".0"} 
                            secondary={row.version_description} 
                            primaryTypographyProps={{
                                fontSize: 14,
                                fontWeight: "bold",
                                mt: -1,
                            }}
                            secondaryTypographyProps={{
                                fontSize: 14,
                                mb: -1,
                            }}
                        />
                    </ListItem>
                </TableCell>
                <TableCell align="center">{row.created.slice(5,-4)}</TableCell>
                <TableCell align="center">{row.test_status}</TableCell>
                <TableCell align="center">{row.approval_status}</TableCell>
                <TableCell align="center">{row.deploy_status}</TableCell>
            </StyledTableRow>
            <TableRow>
                <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 1 }}>
                            <Typography variant="h7" sx={{ fontWeight: "bold" }} >
                                Test Performance
                            </Typography>
                            <Table size="small">
                                <TableHead>
                                <TableRow>
                                    <TableCell>AUC ROC</TableCell>
                                    <TableCell>Gini Norm</TableCell>
                                    <TableCell align="center">KS Score</TableCell>
                                    <TableCell align="right">LogLoss</TableCell>
                                    <TableCell align="right">Rate Top10</TableCell>
                                </TableRow>
                                </TableHead>
                                <TableBody>
                                    <StyledCollapsibleRow>
                                        <TableCell sx={{ color: "gray" }}>
                                            {row.auc_roc}
                                        </TableCell>
                                        <TableCell sx={{ color: "gray" }}>
                                            {row.gini_norm}
                                        </TableCell>
                                        <TableCell align="center" sx={{ color: "gray" }}>
                                            {row.ks_score}
                                        </TableCell>
                                        <TableCell align="right" sx={{ color: "gray" }}>
                                            {row.logloss}
                                        </TableCell>
                                        <TableCell align="right" sx={{ color: "gray" }}>
                                            {row.rate_top10}
                                        </TableCell>
                                    </StyledCollapsibleRow>
                                </TableBody>
                            </Table>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        </React.Fragment>
    );
}

function VersionTable() {
    const data = useSelector((state) => state.version.versions);

    return (
        <React.Fragment>
            <Table size="median">
                <TableHead>
                <TableRow>
                    <StyledTableCell />
                    <StyledTableCell sx={{ maxWidth: "500px", fontWeight: "bold" }}>
                        Name & Description
                    </StyledTableCell>
                    <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                        Created
                    </StyledTableCell>
                    <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                        Test Status
                    </StyledTableCell>
                    <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                        Approval Status
                    </StyledTableCell>
                    <StyledTableCell align="center" sx={{ fontWeight: "bold" }}>
                        Deploy Status
                    </StyledTableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {data.map((row) => (
                    <Row key={row.version_number} row={row}/>
                ))}
                </TableBody>
            </Table>
        </React.Fragment>
    );
}

export default function ModelVersions() {
    return (
      <Container sx={{ py: 4 }} maxWidth="xl">
        <Stack spacing={2}>
            <Typography variant="h6" align="left" sx={{ fontWeight: "bold" }}>
                Manage Model Versions
            </Typography>
            <Paper
              sx={{
                p: 2,
                height: "100%",
              }}
              elevation={2}
            >   
                <VersionTable />
            </Paper>
        </Stack>
      </Container>
    );
}