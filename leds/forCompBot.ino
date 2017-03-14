/*

 Arduino code with LED which uses serial to send commands.
 
 Licensed under GPLv3.
 
 The layout for commands:
 
 0-16: 
 * Control functions, low level like turn on, off, specific indexes.
 
 16-64:
 * Functions for the game
 
 Wiring:

Robot top down:

SECTION|LENGTH

    2|22  3|22



    1|20  0|20
 
 */


#include "FastLED.h"

#include <SPI.h>
#include <Ethernet.h>

byte mac[] = { 
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };  
//the IP address for the shield:
byte ip[] = { 
  10, 39, 66, 177 };    
// the router's gateway address:
byte gateway[] = { 
  10, 0, 0, 1 };
// the subnet:
byte subnet[] = { 
  255, 255, 255, 0 };

#if defined(ARDUINO_AVR_UNO)       
    #define BOARD "Uno"
    #define IS_ETHERNET 0
    #define IS_SERIAL 1
#elif defined(ARDUINO_AVR_ETHERNET)       
    #define BOARD "Ethernet"
    #define IS_ETHERNET 1
    #define IS_SERIAL 0
#else
    #define BOARD "Unknown"
    #define IS_ETHERNET 0
    // assume serial
    #define IS_SERIAL 1
#endif

// uncomment to connect instantly
#define WAITONDELAY (1000)

#define NUM_LEDS (150)
#define DATA_PIN 6

CRGB leds[NUM_LEDS];
#define BRIGHTNESS 127


int is_good = 0;

// enough room for four colors, and four arguments
#define NUM_ARGS (4*3+4)
int args[NUM_ARGS];


#define RGB_args(i0, i1, i2) (CRGB(args[i1], args[i0], args[i2]))


#define MAX_FUNC 256
int func_id, function_runs, prev_func_id;

// use these for functions
#define MAX_VARS 10
int vars[10];

String inputString = "";        // a string to hold incoming data
boolean stringComplete = false; // whether the string is complete

int isEthernet = IS_ETHERNET;
EthernetServer server = EthernetServer(5800);

char startChar = 'A';
char endChar = 'Z';
String bufferString = "";
int MAX_BUFF_SIZE = 200;

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

void setup() {
  Serial.begin(9600);
  Serial.println("Serial start");

  if (isEthernet > 0)
  {
#ifdef WAITONDELAY
    delay(WAITONDELAY);
#endif

    Ethernet.begin(mac, ip, gateway, subnet);
    server.begin();
    Serial.println("Ethernet start");
  }

  LEDS.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);
  LEDS.setBrightness(BRIGHTNESS);
  clear_leds();
  FastLED.show();

  functionArr[0] = _nothing_0;
  functionArr[1] = _off_1;
  functionArr[2] = _on_2;
  functionArr[3] = _fade_3;

  functionArr[16] = _sweep_16;
  functionArr[17] = _cylon_17;
  functionArr[18] = _width_18;
  functionArr[19] = _height_19;
  functionArr[20] = _ambiant_20;
  functionArr[21] = _sin_21;

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

void fademix(CRGB color, int byte) { 
  for(int i = 0; i < NUM_LEDS; i++) {
    leds[i] = mixColor(leds[i], color, byte);
  }
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
  int fr = toaddweight, to = 256 - toaddweight;
  return CRGB((fr*from[0]+to*toadd[0])/256, (fr*from[1]+to*toadd[1])/256, (fr*from[2]+to*toadd[2])/256);
}


int cmp_leds(CRGB a, CRGB b, int channel) {
  if (channel == 3) {
    int sa = (a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);
    int sb = (b[0]*b[0]+b[1]*b[1]+b[2]*b[2]);
    return (sa - sb);
  } 
  else {
    return (a[channel] - b[channel]);
  }
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
  FastLED.show();
}
void _on_2() {
  CRGB color = RGB_args(0, 1, 2);
  for (int i = 0; i < NUM_LEDS; ++i) {
    leds[i] = color;
  }
  FastLED.show();
}

void _fade_3() {
  int fade_rate = args[0]; 
  int delay_rate = args[1];

  fade(fade_rate);

  FastLED.show();
  delay(delay_rate);
}


void _sweep_16() {

  CRGB color = RGB_args(0, 1, 2);
  CRGB tocolor = RGB_args(3, 4, 5);
  int fade_rate = args[6];
  int delay_rate = args[7];

  for (int i = 0; i < NUM_LEDS; ++i) {
    //if (_should_abort()) { return; }

    leds[i] = color;

    FastLED.show();

    fademix(tocolor, fade_rate);
    delay(delay_rate);
  }

  FastLED.show();
}

void cylon_base(int sind, int min, int max, int width, CRGB col, CRGB notcol, int fadev) {
  for (int i = min; i < max; ++i) {
    if (i <= sind + width && i >= sind) {
      leds[i] = mixColor(leds[i], col, fadev);
    } 
    else {
      leds[i] = mixColor(leds[i], notcol, fadev);
    }
  }
}

void _cylon_17() {
  CRGB color = RGB_args(0, 1, 2);
  CRGB notcolor = RGB_args(3, 4, 5);
  int width = args[6]-1;
  int fadev = args[7];
  int wait = args[8];

  int min0 = 0, max0 = 50, min1 = 50, max1 = 100, min2 = 100, max2 = 150;

  int _sl0 = (max0 - min0) - width;
  int _sl1 = (max1 - min1) - width;
  int _sl2 = (max2 - min2) - width;

  if (function_runs == 0) {
    vars[0] = 0;
    vars[1] = 30;
    vars[2] = 0;
  }

  int sind0 = abs(vars[0] - (_sl0)) + min0;
  int sind1 = abs(vars[1] - (_sl1)) + min1;
  int sind2 = abs(vars[2] - (_sl2)) + min2;

  cylon_base(sind0, min0, max0, width, color, notcolor, fadev);
  cylon_base(sind1, min1, max1, width, color, notcolor, fadev);
  cylon_base(sind2, min2, max2, width, color, notcolor, fadev);

  vars[0] = (vars[0] + 1) % (2*(_sl0));
  vars[1] = (vars[1] + 1) % (2*(_sl1));
  vars[2] = (vars[2] + 1) % (2*(_sl2));

  FastLED.show();
  delay(wait);
}

void _width_18() {
  CRGB color = RGB_args(0, 1, 2);
  int width = args[3]-1;
  int wait = args[4];

  cylon_base((NUM_LEDS - width)/2, 0, NUM_LEDS, width, color, CRGB(0, 0, 0), 10);

  FastLED.show();
  delay(wait);
}

void _height_base(int offset, int len, int percent, CRGB pos, CRGB neg) {
  if (len > 0) {
    for (int i = offset; i < offset + len; i++) {
      if (i < offset + (len*percent)/100.0) {
        leds[i] = pos;
      } else {
        leds[i] = neg;
      }
    }
  } else if (len < 0) {
    for (int i = offset - len - 1; i >= offset; i--) {
      if (i > (offset - len - 1) + (len*percent)/100.0) {
        leds[i] = pos;
      } else {
        leds[i] = neg;
      }
    }
  }

}

void _height_19() {
  CRGB colorPos = RGB_args(0, 1, 2);
  CRGB colorNeg = RGB_args(3, 4, 5);
  int percent = args[6];
  
  _height_base(0, 20, percent, colorPos, colorNeg);
  _height_base(20, -20, percent, colorPos, colorNeg);
  _height_base(40, -22, percent, colorPos, colorNeg);
  _height_base(62, -22, percent, colorPos, colorNeg);

  FastLED.show();
}

void _20_base(CRGB c0, CRGB c1, int off, int start, int stop) {
  int step = (stop > start) ? 1 : -1;
  int i = start;
  while (i != stop) {
    if (i > start + step * off) {
      leds[i] = c1;
    } else {
      leds[i] = c0;
    }
    i += step;
  }
} 

void _ambiant_20() {
  //CRGB col0 = RGB_args(0, 1, 2);
  //CRGB col1 = RGB_args(3, 4, 5);
  //int delayv = args[6];
  //int fadev = args[7];
  CRGB col0 = CRGB(50, 100, 50);
  CRGB col1 = CRGB(0, 0, 255);
  int delayv = 60;
  int fadev = 240;
  if (function_runs == 0) {
    vars[0] = 0;
    vars[1] = 0;
    vars[2] = 0;
    vars[3] = 0;
  }
  _20_base(col0, col1, vars[0], 0, 20);
  _20_base(col0, col1, vars[1], 19, 40);
  _20_base(col0, col1, 2+vars[2], 61, 39);
  _20_base(col0, col1, 2+vars[3], 82, 60);

  vars[0] = (vars[0] + 1) % 20;
  vars[1] = (vars[1] + 1) % 20;
  vars[2] = (vars[2] + 1) % 20;
  vars[3] = (vars[3] + 1) % 20;
  FastLED.show();
  fade(fadev);
  delay(delayv);
}

void _sin_base(CRGB col, int deg, int start, int stop) {
  int stp = (stop > start) ? 1 : -1;
  int range = (stop - start) * stp, mid = start + (stop - start)/2;
  double x = range * sin(stp * deg * 3.1415926535 / 180.0);
  int i = start;
  CRGB ctw;
  while (i != stop) {
    int towrite = 255-(int)(255 * abs(x - (i - mid)) / (2.0*range));
    //towrite = 255 * ((towrite * towrite) / (255)) / towrite;
    ctw = col;
    towrite = scale8(towrite, towrite);
    ctw.r = scale8(ctw.r, towrite);
    ctw.g = scale8(ctw.g, towrite);
    ctw.b = scale8(ctw.b, towrite);
    leds[i] = ctw;
    i += stp;
  }
}

void _sin_21() {
  //CRGB col = RGB_args(0, 1, 2);
  //int delayv = args[3];
  CRGB col = CRGB(255, 0, 0);
  int delayv = 1;
  if (function_runs == 0) {
    vars[0] = 0;
  }

  _sin_base(col, vars[0], 0, 20);
  _sin_base(col, vars[0], 39, 19);
  _sin_base(col, vars[0], 62, 39);
  _sin_base(col, vars[0], 84, 62);
  vars[0] = (vars[0] + 1) % 360;

  FastLED.show();
  //delay(delayv);
}

void _bubblesort_128() {
  int ch = args[0];
  if (ch == 0) {
    ch = 1;
  } 
  else if (ch == 1) {
    ch = 0;
  }
  int intensity = args[1];
  if (function_runs == 0) {
    if (ch == 0) {
      random_leds(0, intensity, 0);
    } 
    else if (ch == 1) {
      random_leds(intensity, 0, 0);
    } 
    else if (ch == 2) {
      random_leds(0, 0, intensity);
    } 
    else {
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
  FastLED.show();
}

void parse_serial()
{
  char separator[] = ",";
  char *token;
  int argc = 0;

  if (stringComplete)
  {
    String token;
    token = getValue(inputString, ',', 0);
    int new_func_id = 0;
    if (token != NULL && token != "")
    {
      new_func_id = token.toInt();
      if (new_func_id < 0 || new_func_id >= MAX_FUNC)
      {
        return;
      }
      for (int i = 0; i < NUM_ARGS; ++i)
      {
        token = getValue(inputString, ',', i + 1); //offset by 1 for func_id
        if (token != NULL && token != "")
        {
          args[i] = token.toInt();
        }
        else
        {
          args[i] = 0;
        }
      }

      func_id = new_func_id;
      Serial.print("func_id=");
      Serial.print(func_id);

      for (int i = 0; i < NUM_ARGS; ++i)
      {
        Serial.print(", ");
        Serial.print(i);
        Serial.print(" = ");
        Serial.print(args[i]);
      }
      Serial.println("");

      if (func_id != prev_func_id)
      {
        Serial.println("changed function");
        Serial.println(inputString);
        function_runs = 0;
      }
    }

    inputString = "";
  }
}

void parse_ethernet()
{
  EthernetClient client = server.available();
  if (client == true ) {
    int bytesAvail = client.available();
    Serial.print(bytesAvail);
    Serial.println(" Bytes available");

    while(client.connected()){

        func_id = (int)client.read();
        if (func_id >= 0) {
          for (int i = 0; i < NUM_ARGS; ++i) {
            int a = (int)client.read();
            if(a < 0)
            {
              func_id = prev_func_id;
              return;
            }
            args[i] = a;
          }
          function_runs = 0;
        } 
        else {
          func_id = prev_func_id;
        }
      
    }


  }
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++)
  {
    if (data.charAt(i) == separator || i == maxIndex)
    {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }

  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void readSerialData()
{
  while (Serial.available())
  {
    // get the new byte:

    char inChar = (char)Serial.read();
    if (inChar <= 0)
    {
      return;
    }
    if (inChar == startChar)
    {
      stringComplete = false;
      bufferString = "";
    }
    else if (inChar == endChar)
    {
      inputString = bufferString;
      stringComplete = true;
      bufferString = "";
      return;
    }
    else
    {
      // add it to the bufferString:
      stringComplete = false;
      bufferString += inChar;
      if (bufferString.length() >= MAX_BUFF_SIZE)
      {
        bufferString = "";
      }
    }
  }
}

void loop() {

  //Serial.println("Loop begin");
  /*
  if (isEthernet > 0)
  {
    parse_ethernet();
  }
  else
  {
    readSerialData();
    parse_serial();
  }
*/
  func_id = 21;
  run_function();

  //FastLED.show();

  function_runs += 1;
  prev_func_id = func_id;
}


