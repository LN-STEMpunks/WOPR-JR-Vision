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

#define NUM_LEDS 150
#define DATA_PIN 6

CRGB leds[NUM_LEDS];
#define BRIGHTNESS 255


int is_good = 0;

/*
#define NUM_ARGS 3

int args[NUM_ARGS];
*/

#define MAX_FUNC 256

int func_id, function_runs, prev_func_id;


void (*functionArr[MAX_FUNC])();

void run_function() {
(*functionArr[func_id])(); //calls the function at the index of `index` in the array
}


void setup() {
	Serial.begin(9600);
	LEDS.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
	LEDS.setBrightness(BRIGHTNESS);
	clear_leds();

	functionArr[0] = _nothing_0;
	functionArr[1] = _off_1;
	functionArr[2] = _onR_2;
	functionArr[3] = _onG_3;
	functionArr[4] = _onB_4;

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
		leds[i] = 
		leds[i].nscale8(byte); 
	}
}

void random_leds(int rm, int gm, int bm) {
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = CRGB((random()%256)*gm/256, (random()%256)*rm/256, (random()%256)*bm/256);
	}
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



// Start CONTROL functions
void _nothing_0() {
// nothing
}
void _off_1() {
	clear_leds();
}
void _onR_2() {
	CRGB color = CRGB(255, 0, 0);
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = color;
	}
}
void _onG_3() {
	CRGB color = CRGB(0, 255, 0);
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = color;
	}
}
void _onB_4() {
	CRGB color = CRGB(0, 0, 255);
	for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = color;
	}
}

void _fade_3() { 
	fade(250);
}


void _sweep_16() {
	CRGB nothing = CRGB(0,0,0);
	CRGB color = CRGB(255, 50, 120);

	for (int i = 1; i < NUM_LEDS; ++i) {
		if (_should_abort()) { return; }

		leds[i-1] = nothing;
		leds[i] = color;

		FastLED.show();

		_fade_3();
		delay(5);
	}
	leds[NUM_LEDS-1] = nothing;
	FastLED.show();
}

void _bubblesort_128() {
	if (function_runs == 0) {
		random_leds(0, 0, 255);
	}
	CRGB tmp;
	for (int i = 1; i < NUM_LEDS; ++i) {
		if (cmp_leds(leds[i], leds[i-1], 2) < 0) {
			tmp = leds[i];
			leds[i] = leds[i-1];
			leds[i-1] = tmp;
			FastLED.show();
		}
	}
}



void parse_serial() {
	if (Serial.available() > 0) {
		func_id = (int)Serial.read();
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

