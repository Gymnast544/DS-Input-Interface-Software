/*
DS Driver Master
This is the program that is pre-loaded onto the Pro Micro board. It is the program that is compatible with the Python desktop program
It has 3 modes: (Referred to as mode 0, 1, 2 throughout the program
1. Custom Serial Protocol (default, compatible with builtin input display)
2. Pro Micro board emulates a USB keyboard
3. Pro Micro board emulates a USB gamepad
Copyright 2020 Gymnast544
*/

//Initializing the keyboard and joystick libraries
#include "Keyboard.h"
#include "Joystick.h"
Joystick_ Joystick(JOYSTICK_DEFAULT_REPORT_ID,JOYSTICK_TYPE_GAMEPAD,
  12, 0,                  // Button Count, Hat Switch Count
  false, false, false,     // X and Y, but no Z Axis
  false, false, false,   // No Rx, Ry, or Rz
  false, false,          // No rudder or throttle
  false, false, false);  // No accelerator, brake, or steering


//Defining which pin connects to which button
#define LEFT_SHOULDER_PIN 2
#define DPAD_RIGHT_PIN 3
#define DPAD_UP_PIN 4
#define DPAD_LEFT_PIN 5
#define DPAD_DOWN_PIN 6
#define X_PIN 7
#define Y_PIN 8
#define B_PIN 9
#define SELECT_PIN 10
#define A_PIN 16
#define RIGHT_SHOULDER_PIN 14
#define START_PIN 15
#define XPLUS A3
#define YPLUS A2
#define YMINUS A1
#define XMINUS A0




//Arrays for each pin
int pinstatus[12] = {1,1,1,1,1,1,1,1,1,1,1,1};//Sets all button statuses to pressed, which is the default when the DS is off

int pins[12] = {A_PIN, B_PIN, X_PIN, Y_PIN, DPAD_LEFT_PIN, DPAD_RIGHT_PIN, DPAD_UP_PIN, DPAD_DOWN_PIN, LEFT_SHOULDER_PIN, RIGHT_SHOULDER_PIN, START_PIN, SELECT_PIN};

char pindown[12] = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21};//Bytes which are sent when a button is pressed
char pinup[12] = {30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41};//Bytes which are sent when a button is released
int keys[12] = {'a', 'b', 'x', 'y', KEY_LEFT_ARROW, KEY_RIGHT_ARROW, KEY_UP_ARROW, KEY_DOWN_ARROW, 'l', 'r', KEY_TAB, KEY_RETURN};//Keybindings for mode 2

int mode = 0;//default mode is custom serial interface

//Sending a value between 50 and 60 will change the mode
//50 changes to default mode (1)
//51 changes to keyboard mode (2)
//52 changes to gamepad mode (3)

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

  //Resets the status of each pin
  for (int i = 0; i < 12; i++) {
    pinstatus[i] = 1;
  }

}

void setup() {
  // put your setup code here, to run once:
  resetbuttons();
  if(mode==0){
    Serial.begin(115200);
  }else if(mode==1){
    //do nothing
  }else if(mode==2){
    Joystick.begin();
  }
  
}

void loop(){
  if(mode==0){
    serialInterface();
  }else if(mode==1){
    keyboardInterface();
  }else if(mode==2){
    gamepadInterface();
  }
}

void checkMode(int incomingbyte){
  //Checks any incoming bytes to see if they're a mode switching byte
  if(incomingbyte>49 && incomingbyte<53){
    //the byte is telling us to switch modes
    if(mode!=incomingbyte-50){
      if(incomingbyte-50==2){
        //means we're switching away from joystick mode
        Joystick.end();
      }
      mode = incomingbyte-50;
      resetbuttons();
      //means we're switching modes
      if(mode==2){
        Joystick.begin();
      }
    }
  }else if(incomingbyte==100){
      //Performs the "handshake test"
      //If it receives byte 100, it will send byte 101 - this is the verification that the desktop program uses to verify that it's an Input Interface connected
      Serial.write(101);
    }
}

void checkModeLoop(){
  for (int i=0;i<Serial.available();i++){
    int incomingbyte = Serial.read();
    checkMode(incomingbyte);
  }
}

void serialInterface() {
  for (int i=0;i<Serial.available();i++){
    //Checks all incoming bytes
    int incomingbyte = Serial.read();
    checkMode(incomingbyte);
    //Serial.write(incomingbyte);
    if (incomingbyte<25){
      //Electronically pressing a button
      int buttonnum = incomingbyte-10;
      pinstatus[buttonnum] = -1;//indicating to the input loop that the button is pressed 
      pinMode(pins[buttonnum], OUTPUT);
      digitalWrite(pins[buttonnum], LOW);
    }else{
      //Stopping electronically pressing a button
      int buttonnum = incomingbyte-30;
      pinstatus[buttonnum] = 1;//Setting the button status to released
      pinMode(pins[buttonnum], INPUT);
    }
    
  }
  for (int i = 0; i < 12; i++) {
    if (pinstatus[i] > -1) {
      //getting input
      int pinread = digitalRead(pins[i]);
      if (pinread != pinstatus[i]) {
        if (pinread) {
          Serial.write(pinup[i]);
        }
        else {
          Serial.write(pindown[i]);
        }
      }
      pinstatus[i] = pinread;
    }

  }
}
void keyboardInterface() {
  checkModeLoop();
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


void gamepadInterface() {
  checkModeLoop();
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
