#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

int main()
{
    // Load training data
    Mat data = (Mat_<float>(4, 2) << 1.2, 3.3,
                                     2.2, 4.1,
                                     3.1, 1.7,
                                     1.7, 6.8);
    Mat labels = (Mat_<int>(4, 1) << 0, 0, 1, 1);

    // Train decision tree
    Ptr<ml::DTrees> dtree = ml::DTrees::create();
    dtree->train(data, ml::ROW_SAMPLE, labels);

    // Test model on new data
    Mat test_data = (Mat_<float>(1, 2) << 2.8, 5.6);
    Mat response;
    dtree->predict(test_data, response);

    cout << "Prediction: " << response.at<float>(0) << endl;

    return 0;
}