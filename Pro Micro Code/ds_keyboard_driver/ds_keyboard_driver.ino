/*
DS Keyboard Driver
This is a program you can load onto the input interface which makes it *only* emulate a keyboard (Mode 2 of the master driver)

Copyright 2020 Gymnast544
*/

#include "Keyboard.h"


#define LEFT_SHOULDER_PIN 2
#define DPAD_RIGHT_PIN 3
#define DPAD_UP_PIN 4 // not working
#define DPAD_LEFT_PIN 5
#define DPAD_DOWN_PIN 6
#define X_PIN 7
#define Y_PIN 8
#define B_PIN 9
#define SELECT_PIN 10
#define A_PIN 16
#define RIGHT_SHOULDER_PIN 14
#define START_PIN 15

int pinstatus[12] = {1,1,1,1,1,1,1,1,1,1,1,1};
int pins[12] = {A_PIN, B_PIN, X_PIN, Y_PIN, DPAD_LEFT_PIN, DPAD_RIGHT_PIN, DPAD_UP_PIN, DPAD_DOWN_PIN, LEFT_SHOULDER_PIN, RIGHT_SHOULDER_PIN, START_PIN, SELECT_PIN};
int keys[12] = {'a', 'b', 'x', 'y', KEY_LEFT_ARROW, KEY_RIGHT_ARROW, KEY_UP_ARROW, KEY_DOWN_ARROW, 'l', 'r', KEY_TAB, KEY_RETURN};

void resetbuttons() {
  //Setting all button modes to input
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
  pinMode(8, INPUT);
  pinMode(9, INPUT);
  pinMode(10, INPUT);
  pinMode(14, INPUT);
  pinMode(15, INPUT);
  pinMode(16, INPUT);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  for (int i = 0; i < 12; i++) {
    pinstatus[i] = 1;
  }

}

void setup(){
  resetbuttons();
}
void loop() {
  for (int i = 0; i < 12; i++) {
    if (pinstatus[i] > -1) {
      //getting input
      int pinread = digitalRead(pins[i]);
      if (pinread != pinstatus[i]) {
        if (pinread) {
          Keyboard.release(keys[i]);
        }
        else {
          Keyboard.press(keys[i]);
        }
      }
      pinstatus[i] = pinread;
    }

  }
}
