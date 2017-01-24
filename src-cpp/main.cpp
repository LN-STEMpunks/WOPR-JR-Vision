
#include <cv.h>
#include <highgui.h>

using namespace std;

int camera_port = 0;


int main(int argc, char *argv[]) {

	cv::Mat img;
	cv::VideoCapture camera(camera_port);

	cv::namedWindow("w", cv::WINDOW_AUTOSIZE);
	while (true) {
		camera >> img;
		cv::imshow("w", img);
		cv::waitKey(1);
		
	}

	return 0;
}
