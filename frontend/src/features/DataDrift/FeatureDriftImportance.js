import React from "react";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Scatter } from "react-chartjs-2";
import { faker } from "@faker-js/faker";

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export const options = {
  scales: {
    y: {
      beginAtZero: true,
      max: 1,
      min: 0,
      title: {
        display: true,
        text: "Drift",
      },
    },
    x: {
      beginAtZero: true,
      max: 1,
      min: 0,
      title: {
        display: true,
        text: "Importance",
      },
    },
  },
  plugins: {
    tooltip: {
      displayColors: false,
      padding: 10,
      callbacks: {
        title: function (context) {
          return context[0].raw.id;
        },
        label: function (context) {
          return [`Importance: ${context.raw.x}`, `Drift: ${context.raw.y}`];
        },
      },
    },
  },
};

export const data = {
  datasets: [
    {
      label: "Healthy",
      data: Array.from({ length: 20 }, () => ({
        id: "Feature " + faker.datatype.string(5),
        x: faker.datatype.float({ min: 0, max: 1 }),
        y: faker.datatype.float({ min: 0, max: 0.5 }),
      })),
      backgroundColor: "green",
    },
    {
      label: "At risk",
      data: Array.from({ length: 10 }, () => ({
        id: "Feature " + faker.datatype.string(5),
        x: faker.datatype.float({ min: 0, max: 1 }),
        y: faker.datatype.float({ min: 0, max: 0.5 }),
      })),
      backgroundColor: "yellow",
    },
    {
      label: "Failing",
      data: Array.from({ length: 10 }, () => ({
        id: "Feature " + faker.datatype.string(5),
        x: faker.datatype.float({ min: 0, max: 1 }),
        y: faker.datatype.float({ min: 0, max: 0.5 }),
      })),
      backgroundColor: "red",
    },
  ],
};

export function FeatureDriftImportance() {
  return <Scatter options={options} data={data} />;
}
