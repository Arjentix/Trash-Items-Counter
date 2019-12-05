/**
 * @author: Polyakov Daniil
 * @mail: arjentix@gmail.com
 * @github: Arjentix
 * @date: 05.12.2019
 */

#include <GyverTM1637.h>

#define MINUS 0x40 // Minus symbol

const int CLK = 2; // Set the CLK pin connection to the display
const int DIO = 3; // Set the DIO pin connection to the display

GyverTM1637 display(CLK, DIO);

void setup() {
  Serial.begin(9600);
  display.brightness(7);  // Set the diplay to maximum brightness
  display.displayByte(MINUS, MINUS, MINUS, MINUS);
}

void loop() {
  if (Serial.available()) {
    int count = Serial.parseInt();
    display.displayInt(count); // Display
  }
}
