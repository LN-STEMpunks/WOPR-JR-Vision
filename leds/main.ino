#include "FastLED.h"

#define NUM_LEDS 150
#define DATA_PIN 6

CRGB leds[NUM_LEDS];
#define BRIGHTNESS 120

int func_id, a0, a1, a2, a3;

char terminator = ';';

void clear_leds()
{
    for (int i = 0; i < NUM_LEDS; ++i) {
		leds[i] = CRGB(0, 0, 0);
    }
    FastLED.show();
}

// Start CONTROL functions
void _nothing_0() {
  // nothing
}
void _off_1() {
	clear_leds();
}
void _on_2() {
    for (int i = 0; i < NUM_LEDS; ++i) {
        leds[i] = CRGB(a1, a0, a2);
    }
}
void _on_index_3() {
    leds[a3] = CRGB(a1, a0, a2);
}

int parse_serial() {
	func_id = Serial.parseInt();
	a0 = Serial.parseInt();
	a1 = Serial.parseInt();
	a2 = Serial.parseInt();
	a3 = Serial.parseInt();
	if (Serial.read() != terminator) {
          return 1;
        }
	return 0;
}

void setup() {
    Serial.begin(9600);
    LEDS.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
    LEDS.setBrightness(BRIGHTNESS);
    clear_leds();
}


void loop() {
        while (Serial.available()  > 0) {
  	if (parse_serial() == 0) {
          switch (func_id) {
             case 0:
               _nothing_0();
               break;
             case 1:
               _off_1();
               break;
             case 2:
               _on_2();
               break;
             case 3:
               _on_index_3();
               break;
           }
  	}
        FastLED.show();
        }
        
}

