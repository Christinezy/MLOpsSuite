import * as React from "react";
import { useTheme } from "@mui/material/styles";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Label,
  ResponsiveContainer,
  CartesianGrid,
  Tooltip,
} from "recharts";
import Typography from "@mui/material/Typography";

export default function Chart(props) {
  const { type, data, title } = props;
  const theme = useTheme();

  return (
    <React.Fragment>
      <Typography variant="h7" sx={{ fontWeight: "bold" }}>
        {props.title}
      </Typography>
      <br></br>
      <ResponsiveContainer>
        <LineChart
          data={data}
          margin={{
            top: 16,
            right: 16,
            bottom: 0,
            left: 24,
          }}
        >
          <CartesianGrid strokeDasharray="10 10" />
          <XAxis
            dataKey="timestamp"
            stroke={theme.palette.text.secondary}
            style={theme.typography.body2}
          />
          <YAxis
            stroke={theme.palette.text.secondary}
            style={theme.typography.body2}
            domain={["dataMin-0.01", "dataMax+0.001"]}
          ></YAxis>
          <Tooltip />
          <Line
            isAnimationActive={true}
            type="monotone"
            dataKey={type}
            stroke={theme.palette.primary.main}
            dot={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </React.Fragment>
  );
}
