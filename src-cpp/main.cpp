

#include "cv.h"
#include "highgui.h"

#include <chrono>
#include <cmath>

using namespace std;
using namespace std::chrono;


int camera_port = 0;

int scaleFactor = 4;

cv::Size size(160, 120),
         blur(4, 4);

double hueMin = 73.26,
	   hueMax = 120.20,
	   satMin = 95.09,
	   satMax = 165.78,
	   lumMin = 100.62,
	   lumMax = 320.48;

void twoLargestContours(vector<vector<cv::Point>> contours, int& a, int& b) {
	int idx1 = 0, idx2 = 0, area1 = -1, area2 = -1;
	double areai;
	for (int i = 0; i < contours.size(); ++i) {
		areai = cv::contourArea(contours[i]);
		if (areai > area1) {
			area2 = area1;
			idx2 = idx1;

			area1 = areai;
			idx1 = i;
		} else if (areai > area2) {
			area2 = areai;
			idx2 = i;
		}
	}
	a = idx1; b = idx2;
}

cv::Point2f findContourCenter(vector<cv::Point> contour) {
	cv::Moments mu = cv::moments( contour, false ); 
	return cv::Point2f( mu.m10/mu.m00 , mu.m01/mu.m00 );
}

void process(cv::Mat& source0, vector<vector<cv::Point>>& contours) {
	
	cv::blur(source0, source0, blur);
	
	cv::cvtColor(source0, source0, CV_BGR2HLS);
	cv::inRange(source0, cv::Scalar(hueMin, lumMin, satMin), cv::Scalar(hueMax, lumMax, satMax), source0);
	cv::findContours( source0, contours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_TC89_KCOS);
	
}

int main(int argc, char *argv[]) {
	cout << "Welcome to WOPR-JR-Vision" << endl;
	printf ("OpenCV version: %d, %d\n", CV_MAJOR_VERSION, CV_MINOR_VERSION);
	cv::Mat img, toshow;
        vector<vector<cv::Point>> contours;
	cv::VideoCapture camera(camera_port);

    camera.set(CV_CAP_PROP_AUTO_EXPOSURE, 0);
	camera.set(CV_CAP_PROP_EXPOSURE, 1.0); 
	//camera.set(CV_CAP_PROP_GAIN, 0.9); 


	cout << "Camera Exposure: " << camera.get(CV_CAP_PROP_EXPOSURE) << endl;

	high_resolution_clock::time_point st, et;

	cv::namedWindow("w", cv::WINDOW_AUTOSIZE);

	int contour1, contour2;
	
	while (true) {
		st = high_resolution_clock::now();
		camera >> img;

		cv::resize(img, img, size);
		toshow = img.clone();
		process(img, contours);
		
		if (contours.size() >= 2) {
			twoLargestContours(contours, contour1, contour2);

			cv::drawContours(toshow, contours, contour1, cv::Scalar(255, 0, 0));
			cv::drawContours(toshow, contours, contour2, cv::Scalar(255, 0, 0));

			cv::Point2f avgPoint = (findContourCenter(contours[contour1]) + findContourCenter(contours[contour2]));

			avgPoint.x /= 2.0;
			avgPoint.y /= 2.0;

			cv::circle(toshow, avgPoint, 10, cv::Scalar(0, 0, 255));
		}

		//printf("\rTime: %f", et-st);
		cv::imshow("w", toshow);
		
		cv::waitKey(1);
		et = high_resolution_clock::now();
		cout << "FPS: " << pow(10.0, 6) / (duration_cast<microseconds>(et -st).count()) << "\r";
		fflush(stdout);
	}

	return 0;
}
