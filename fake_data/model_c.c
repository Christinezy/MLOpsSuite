#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Define the activation function
double sigmoid(double x) {
    return 1 / (1 + exp(-x));
}

int main() {
    // Define the input data
    double inputs[3][2] = {{0,0}, {0,1}, {1,0}};
    double outputs[3] = {0, 1, 1};

    // Define the weights and biases
    double w1 = 0.5, w2 = 0.5, b = 0.5;

    // Define the learning rate
    double lr = 0.1;

    // Train the model
    for (int i = 0; i < 1000; i++) {
        // Choose a random input
        int index = rand() % 3;
        double x1 = inputs[index][0];
        double x2 = inputs[index][1];
        double y = outputs[index];

        // Calculate the predicted output
        double z = w1 * x1 + w2 * x2 + b;
        double a = sigmoid(z);

        // Calculate the error
        double error = y - a;

        // Update the weights and biases
        w1 += lr * error * a * (1 - a) * x1;
        w2 += lr * error * a * (1 - a) * x2;
        b += lr * error * a * (1 - a);

        // Print the error
        printf("Error: %f\n", fabs(error));
    }

    // Predict some outputs
    double x1 = 1, x2 = 1;
    double z = w1 * x1 + w2 * x2 + b;
    double a = sigmoid(z);
    printf("Input: %f %f\nOutput: %f\n", x1, x2, a);

    return 0;
}