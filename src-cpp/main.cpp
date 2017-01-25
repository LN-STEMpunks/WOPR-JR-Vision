
#include <cv.h>
#include <highgui.h>
#include "opencv2/gpu/gpu.hpp"

#include <chrono>
#include <cmath>

using namespace std;
using namespace std::chrono;


int camera_port = 0;

int scaleFactor = 4;

cv::Size size(160*scaleFactor, 120*scaleFactor);

bool compareContours(vector<cv::Point> a, vector<cv::Point> b) {
	return cv::contourArea(a, false) < cv::contourArea(b, false);
}

cv::Point2f findContourCenter(vector<cv::Point> contour) {
	cv::Moments mu = cv::moments( contour, false ); 
	return cv::Point2f( mu.m10/mu.m00 , mu.m01/mu.m00 );
}

void process(cv::Mat& source0, vector<vector<cv::Point>>& contours) {
	cv::Size blur(9, 9);
	//cv::resize(source0, source0, size);
	cv::blur(source0, source0, blur);
	
	double hue[] = {73.26, 94.20}, saturation[] = {64.09, 165.78}, luminance[] = {140.62, 221.48};
	
	

	cv::cvtColor(source0, source0, CV_BGR2HLS);
	cv::inRange(source0, cv::Scalar(hue[0], luminance[0], saturation[0]), cv::Scalar(hue[1], luminance[1], saturation[1]), source0);

	
	cv::findContours( source0, contours, CV_RETR_LIST, CV_CHAIN_APPROX_SIMPLE);
	
	sort(contours.begin(), contours.end(), compareContours);
	
}

int main(int argc, char *argv[]) {
	cout << "Welcome to WOPR-JR-Vision" << endl;
	cout<<cv::gpu::getCudaEnabledDeviceCount()<<endl;

	cv::Mat img, toshow;
        vector<vector<cv::Point>> contours;
	cv::VideoCapture camera(camera_port);

	high_resolution_clock::time_point st, et;

	cv::namedWindow("w", cv::WINDOW_AUTOSIZE);
	while (true) {
		st = high_resolution_clock::now();
		camera >> img;
		cv::resize(img, img, size);
		toshow = img.clone();
		process(img, contours);
		cv::drawContours(toshow, contours, contours.size()-1, cv::Scalar(255, 0, 0));
		cv::drawContours(toshow, contours, contours.size()-2, cv::Scalar(255, 0, 0));


		cv::Point2f avgPoint = (findContourCenter(contours[contours.size()-1]) + findContourCenter(contours[contours.size()-2]));
		avgPoint.x /= 2.0;
		avgPoint.y /= 2.0;
		cv::circle(toshow, avgPoint, 10, cv::Scalar(0, 0, 255));

		et = high_resolution_clock::now();
		//printf("\rTime: %f", et-st);
		cout << pow(10.0, 6) / (duration_cast<microseconds>(et -st).count()) << "\r";
		fflush(stdout);
		cv::imshow("w", toshow);
		cv::waitKey(1);
		
	}

	return 0;
}
