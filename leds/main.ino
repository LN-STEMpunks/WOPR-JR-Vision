/*

Arduino code with LED which uses serial to send commands.

Licensed under GPLv3.

The layout for commands:

0-16: 
* Control functions, low level like turn on, off, specific indexes.

16-64:
* Functions for the game



*/


#include "FastLED.h"

#include <SPI.h>
#include <Ethernet.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };  
//the IP address for the shield:
byte ip[] = { 10, 39, 66, 177 };    
// the router's gateway address:
byte gateway[] = { 10, 0, 0, 1 };
// the subnet:
byte subnet[] = { 255, 255, 255, 0 };



#define NUM_LEDS 150
#define DATA_PIN 6

CRGB leds[NUM_LEDS];
#define BRIGHTNESS 255


int is_good = 0;


#define NUM_ARGS 5
int args[NUM_ARGS];

#define RGB_args(i0, i1, i2)


#define MAX_FUNC 256
int func_id, function_runs, prev_func_id;


CRGB nothing = CRGB(0,0,0);
CRGB red = CRGB(0,255,0);
CRGB green = CRGB(255,0,0);
CRGB blue = CRGB(0,0,255);

CRGB white = CRGB(255,255,255);
//todo add more colors



void (*functionArr[MAX_FUNC])();

void run_function() {
(*functionArr[func_id])(); //calls the function at the index of `index` in the array
}

EthernetServer server = EthernetServer(23);

void setup() {
	//Serial.begin(9600);
	Ethernet.begin(mac, ip, gateway, subnet);
	server.begin();


	LEDS.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
	LEDS.setBrightness(BRIGHTNESS);
	clear_leds();

	functionArr[0] = _nothing_0;
	functionArr[1] = _off_1;
	functionArr[2] = _on_2;
	functionArr[3] = _fade_3;

	functionArr[16] = _sweep_16;

	functionArr[128] = _bubblesort_128;
}


//char startchar = '@', terminator = ';';

void clear_leds()
{
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = CRGB(0, 0, 0);
	}
}

bool _should_abort() {
	return Serial.available() > 0;
}

void fade(int byte) { 
	for(int i = 0; i < NUM_LEDS; i++) {
		for (int j = 0; j < 3; ++j) {
			leds[i][j] = (leds[i][j]*byte) / 256;
		}
	}
}

void random_leds(int rm, int gm, int bm) {
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = CRGB((random()%256)*gm/256, (random()%256)*rm/256, (random()%256)*bm/256);
	}
}

CRGB mixColor(CRGB from, CRGB toadd, int toaddweight) {
	return CRGB(from[0]+(toadd[0]*toaddweight)/256, from[1]+(toadd[1]*toaddweight)/256, from[2]+(toadd[2]*toaddweight)/256)
}


int cmp_leds(CRGB a, CRGB b, int channel) {
	if (channel == 3) {
		int sa = (a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);
		int sb = (b[0]*b[0]+b[1]*b[1]+b[2]*b[2]);
		return (sa - sb);
	} else {
		return (a[channel] - b[channel]);
	}
}

CRGB getColorFromArgs() {
	return CRGB(args[1], args[0], args[2]);
}

bool areArgsZero() {
	for (int i = 0; i < NUM_ARGS; ++i) {
		if (args[i] != 0) {
			return false;
		}
	}
	return true;
}


// Start CONTROL functions
void _nothing_0() {
// nothing
}
void _off_1() {
	clear_leds();
}
void _on_2() {
	CRGB color = getColorFromArgs();
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = color;
	}
}

void _fade_3() {
	int fade_rate = 250; 
	int delay_rate = args[1];
	if (args[0] != 0) {
		fade_rate = args[0];
	}
	fade(250);
	delay(delay_rate);
}


void _sweep_16() {
	
	CRGB color = getColorFromArgs();
	int fade_rate = args[3];
	int delay_rate = args[4];

	for (int i = 0; i < NUM_LEDS; ++i) {
		if (_should_abort()) { return; }

		leds[i] = color;

		FastLED.show();

		fade(fade_rate);
		delay(delay_rate);
	}
	FastLED.show();
}

void _bubblesort_128() {
	int ch = args[0];
	if (ch == 0) {
		ch = 1;
	} else if (ch == 1) {
		ch = 0;
	}
	int intensity = args[1];
	if (function_runs == 0) {
		if (ch == 0) {
			random_leds(0, intensity, 0);
		} else if (ch == 1) {
			random_leds(intensity, 0, 0);
		} else if (ch == 2) {
			random_leds(0, 0, intensity);
		} else {
			random_leds(intensity, intensity, intensity);
		}
	}
	CRGB tmp;
	for (int i = 1; i < NUM_LEDS; ++i) {
		if (cmp_leds(leds[i], leds[i-1], ch) < 0) {
			tmp = leds[i];
			leds[i] = leds[i-1];
			leds[i-1] = tmp;
			FastLED.show();
		}
	}
}



void parse_serial() {
	EthernetClient client = server.available();
	if (client == true) {
		func_id = (int)client.read();
		for (int i = 0; i < NUM_ARGS; ++i) {
			args[i] = (int)client.read();
		}
		//func_id = 2;
		function_runs = 0;
	}
}

void loop() {
	
	parse_serial();

	run_function();

	FastLED.show();

	function_runs += 1;
	prev_func_id = func_id;
}

