import * as React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { Stack, Box } from "@mui/material";
import Chart from "./Chart";
import CardActionArea from "@mui/material/CardActionArea";
import Paper from "@mui/material/Paper";
import { useState, useEffect } from "react";
import {
  retrieveDataDriftThunk,
  selectDataDrift,
  selectDataDriftLatest,
  selectDataDriftLoading,
} from "../sliceDataDrift";
import { LoadingButton } from "@mui/lab";
import RefreshIcon from '@mui/icons-material/Refresh';
import { useSelector, useDispatch } from "react-redux";

export function metricsArray(latestDrift) {
  let rows = [
    {
      id: 1,
      title: "Log Loss",
      key: "logloss",
      number: latestDrift?.logloss?.toPrecision(2),
    },
    {
      id: 2,
      title: "AUC ROC",
      key: "auc_roc",
      number: latestDrift?.auc_roc?.toPrecision(2),
    },
    {
      id: 3,
      title: "KS Score",
      key: "ks_score",
      number: latestDrift?.ks_score?.toPrecision(2),
    },
    {
      id: 4,
      title: "Gini Norm",
      key: "gini_norm",
      number: latestDrift?.gini_norm?.toPrecision(2),
    },
    {
      id: 5,
      title: "Rate Top 10",
      key: "rate_top10",
      number: latestDrift?.rate_top10?.toPrecision(2),
    },
  ];
  return rows;
}

export function Metrics(props) {
  const { metric, switchContent } = props;
  return (
    <Grid item xs={2}>
      <CardActionArea onClick={() => switchContent(metric)}>
        <Card sx={{ display: "flex" }}>
          <CardContent sx={{ flex: 1 }}>
            <Typography
              variant="subtitle1"
              color="text.secondary"
              sx={{ textAlign: "center" }}
            >
              {metric.title}
            </Typography>
            <Typography variant="h4" sx={{ textAlign: "center" }}>
              {metric.number}
            </Typography>
          </CardContent>
        </Card>
      </CardActionArea>
    </Grid>
  );
}

export default function DriftMetrics() {
  const modelId = window.location.href.substr(window.location.href.length - 1);
  const [content, setContent] = useState("logloss");
  const [contentTitle, setContentTitle] = useState("Log Loss");

  const switchContent = (metric) => {
    setContent(() => metric.key);
    setContentTitle(() => metric.title);
  };
  const data = useSelector(selectDataDrift);
  const latestDrift = useSelector(selectDataDriftLatest);
  const loadingDataDrift = useSelector(selectDataDriftLoading);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(retrieveDataDriftThunk(modelId));
  }, [dispatch, modelId]);

  return (
    <React.Fragment>
      <Box 
        sx={{
          display: "flex",
          justifyContent: "right",  
          mt: 2
        }}
      >
        <LoadingButton
          loading={loadingDataDrift}
          onClick={() => dispatch(retrieveDataDriftThunk(modelId))}
        >
          <RefreshIcon />
        </LoadingButton>
      </Box>
      <Container sx={{ py: 4 }} maxWidth="xl">
        <Stack spacing={4}>
          <Grid container spacing={2} justifyContent="center">
            {metricsArray(latestDrift).map((drift) => (
              <Metrics
                key={drift.title}
                metric={drift}
                switchContent={switchContent}
              />
            ))}
          </Grid>
          <Grid item xs={12} md={8} lg={9}>
            <Paper
              sx={{
                p: 2,
                display: "flex",
                flexDirection: "column",
                height: 500,
              }}
            >
              <Chart type={content} title={contentTitle} data={data} />
            </Paper>
          </Grid>
        </Stack>
      </Container>
    </React.Fragment>
  );
}
