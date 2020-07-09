/*
DS Gamepad Only Driver
This program makes the DS Input Interface *only* emulate a gamepad (equivalent of Mode 2 in the master program)
Copyright 2020 Gymnast544
*/


#include "Joystick.h"
Joystick_ Joystick(JOYSTICK_DEFAULT_REPORT_ID,JOYSTICK_TYPE_GAMEPAD,
  12, 0,                  // Button Count, Hat Switch Count
  false, false, false,     // X and Y, but no Z Axis
  false, false, false,   // No Rx, Ry, or Rz
  false, false,          // No rudder or throttle
  false, false, false);  // No accelerator, brake, or steering

  
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
int pins[12] = {A_PIN, B_PIN, X_PIN, Y_PIN, DPAD_LEFT_PIN, DPAD_RIGHT_PIN, DPAD_UP_PIN, DPAD_DOWN_PIN, LEFT_SHOULDER_PIN, RIGHT_SHOULDER_PIN, START_PIN, SELECT_PIN}; //This determines the order of the buttons as windows sees it

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
  Joystick.begin();
}
void loop() {
  for (int i = 0; i < 12; i++) {
    if (pinstatus[i] > -1) {
      //getting input
      int pinread = digitalRead(pins[i]);
      if (pinread != pinstatus[i]) {
        if (pinread) {
          Joystick.releaseButton(i);
        }
        else {
          Joystick.pressButton(i);
        }
      }
      pinstatus[i] = pinread;
    }

  }
}
