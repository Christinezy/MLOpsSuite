import * as React from 'react';
import Typography from '@mui/material/Typography';
import Title from './Title';
import Container from '@mui/material/Container';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ArrowDropDownCircleSharpIcon from '@mui/icons-material/ArrowDropDownCircleSharp';
import ErrorRoundedIcon from '@mui/icons-material/ErrorRounded';
import Box from '@mui/material/Box';
import Stack from "@mui/material/Stack";
import { useSelector } from "react-redux";


export function ActiveDeployments() {
  const activeProjects = useSelector((state) => state.projectlist.activeProjects);
  return (
    <React.Fragment>  
      <Container maxWidth="sm" sx={{bgcolor: 'white'}}>
        <Title>Active Projects</Title>
        <Box sx={{ height: '24px' }} />
        <Typography align="center" component="p" variant="h4" >
          {activeProjects}
        </Typography>
      </Container>
    </React.Fragment>
  );
}

export function Summary(props) {
  const iconFont = "20px";
  const font = "15px";
  return (
    <React.Fragment>
      <Title>{props.title}</Title>   
        <Container
          sx={{
            height: "100%",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Stack 
            spacing={0}
            justifyContent="center"
            alignItems="center"
          >
            <ListItem sx={{ width: "45%" }}>
              <ListItemIcon>
                <CheckCircleIcon sx={{ color:'#4caf50', fontSize: iconFont }}/>  
              </ListItemIcon>
              <ListItemText
                primary={props.data[0].toString() + " Passing"}
                primaryTypographyProps={{
                  fontSize: font,
                  fontWeight: 'medium',
                  lineHeight: '1px',
                }}
              />
            </ListItem>

            <ListItem sx={{ width: "45%" }}>
              <ListItemIcon>
              <ArrowDropDownCircleSharpIcon sx={{ color: "#FFBF00", fontSize: iconFont }}/>
              </ListItemIcon>
              <ListItemText
                primary={props.data[1].toString() + " At Risk"}
                primaryTypographyProps={{
                  fontSize: font,
                  fontWeight: 'medium',
                  lineHeight: '1px',
                }}
              />
            </ListItem>

            <ListItem 
              sx={{ width: "45%" }}>
              <ListItemIcon>
                <ErrorRoundedIcon sx={{ color: "#ef5350", fontSize: iconFont }}/>
              </ListItemIcon>
              <ListItemText
                primary={props.data[2].toString() + " Failing"}
                primaryTypographyProps={{
                  fontSize: font,
                  fontWeight: 'medium',
                  lineHeight: '1px',
                }}
              />
            </ListItem>
          </Stack>
        </Container>
    </React.Fragment>
  );
}


