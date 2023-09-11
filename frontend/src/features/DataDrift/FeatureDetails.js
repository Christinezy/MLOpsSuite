import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { faker } from "@faker-js/faker";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export const options = {
  responsive: true,
  scales: {
    y: {
      ticks: {
        min: 0,
        max: 100, // Your absolute max value
        callback: function (value) {
          return value + "%"; // convert it to percentage
        },
      },
      title: {
        display: true,
        text: "Percentage of records",
      },
    },
    x: {
      title: {
        display: true,
        text: "Grades",
      },
    },
  },
  plugins: {
    legend: {
      position: "top",
    },
  },
};

const labels = ["A", "B", "C", "D", "E", "F", "G"];

export const data = {
  labels,
  datasets: [
    {
      label: "Training",
      data: labels.map(() => faker.datatype.number({ min: 0, max: 100 })),
      backgroundColor: "rgba(255, 99, 132, 0.5)",
    },
    {
      label: "Scoring",
      data: labels.map(() => faker.datatype.number({ min: 0, max: 100 })),
      backgroundColor: "rgba(53, 162, 235, 0.5)",
    },
  ],
};

export function FeatureDetails() {
  return <Bar options={options} data={data} />;
}
