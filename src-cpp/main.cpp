
#include <cv.h>
#include <highgui.h>

using namespace std;

int camera_port = 0;

bool compareContours(vector<cv::Point> a, vector<cv::Point> b) {
	return cv::contourArea(a, false) < cv::contourArea(b, false);
}

void process(cv::Mat& source0, vector<vector<cv::Point>>& contours) {
	cv::Size size(320, 240);
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

	cv::Mat img, toshow;
        vector<vector<cv::Point>> contours;
	cv::VideoCapture camera(camera_port);

	cv::namedWindow("w", cv::WINDOW_AUTOSIZE);
	while (true) {
		camera >> img;
		toshow = img.clone();
		process(img, contours);
		cv::drawContours(toshow, contours, contours.size()-1, cv::Scalar(255, 0, 0));
		cv::drawContours(toshow, contours, contours.size()-2, cv::Scalar(255, 0, 0));
		cv::imshow("w", toshow);
		cv::waitKey(1);
		
	}

	return 0;
}
