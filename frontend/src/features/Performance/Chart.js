import * as React from 'react';
import { useTheme } from '@mui/material/styles';
import { LineChart, Line, XAxis, YAxis, Label, ReferenceLine, 
         ResponsiveContainer, CartesianGrid, Tooltip } from 'recharts';
import Typography from '@mui/material/Typography';


export default function Chart(props) {
  const theme = useTheme();
  return (
    <React.Fragment>
      <Typography variant="h7" sx={{ fontWeight: "bold", mb: 3 }}>{props.title}</Typography>
      <ResponsiveContainer>
        <LineChart
          data={props.data}
          margin={{
            top: 16,
            right: 16,
            bottom: 0,
            left: 24,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            stroke={theme.palette.text.secondary}
            style={theme.typography.body2}
          />
          <YAxis
            stroke={theme.palette.text.secondary}
            style={theme.typography.body2}
            domain={props.domain}
          >
            <Label
              angle={270}
              position="left"
              style={{
                textAnchor: 'middle',
                fill: theme.palette.text.primary,
                ...theme.typography.body1,
              }}
            >
              {props.title}
            </Label>
          </YAxis>
          <ReferenceLine y={props.threshold} stroke="red">
            <Label value={props.threshold} offset={4} position="top" />
          </ReferenceLine>
          <Tooltip />
          <Line
            isAnimationActive={true}
            type="monotone"
            dataKey="value"
            stroke={theme.palette.primary.main}
            dot={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </React.Fragment>
  );
}
