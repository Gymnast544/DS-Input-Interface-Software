/*
  DS TAS Master
  This is the program that is pre-loaded onto the Pro Micro board. It is the program that is compatible with the Python desktop program
  It has 4 modes: (Referred to as mode 0, 1, 2, 3 throughout the program)
  1. Custom Serial Protocol (default, compatible with builtin input display)
  2. Pro Micro board emulates a USB keyboard
  3. Pro Micro board emulates a USB gamepad
  4. TAS Mode

  TAS Mode requires the addition of two wires to be soldered to work, see the hardware installation instructions for more info
  Copyright 2020 Gymnast544
*/

//Initializing the keyboard and joystick libraries
#include "Keyboard.h"
#include "Joystick.h"
Joystick_ Joystick(JOYSTICK_DEFAULT_REPORT_ID, JOYSTICK_TYPE_GAMEPAD,
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
#define PWR A0

#define SYNC 1




//Arrays for each pin
int pinstatus[12] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1}; //Sets all button statuses to pressed, which is the default when the DS is off

int pins[12] = {A_PIN, B_PIN, X_PIN, Y_PIN, DPAD_LEFT_PIN, DPAD_RIGHT_PIN, DPAD_UP_PIN, DPAD_DOWN_PIN, LEFT_SHOULDER_PIN, RIGHT_SHOULDER_PIN, START_PIN, SELECT_PIN};

char pindown[12] = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21};//Bytes which are sent when a button is pressed
char pinup[12] = {30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41};//Bytes which are sent when a button is released
int keys[12] = {'a', 'b', 'x', 'y', KEY_LEFT_ARROW, KEY_RIGHT_ARROW, KEY_UP_ARROW, KEY_DOWN_ARROW, 'l', 'r', KEY_TAB, KEY_RETURN};//Keybindings for mode 2

int mode = 0;//default mode is custom serial interface

//Sending a value between 50 and 60 will change the mode
//50 changes to default mode (1)
//51 changes to keyboard mode (2)
//52 changes to gamepad mode (3)
//53 changes to TAS mode

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
  if (mode == 0) {
    Serial.begin(115200);
  } else if (mode == 1) {
    //do nothing
  } else if (mode == 2) {
    Joystick.begin();
  }

}

void loop() {
  if (mode == 0) {
    serialInterface();
  } else if (mode == 1) {
    keyboardInterface();
  } else if (mode == 2) {
    gamepadInterface();
  } else if (mode == 3) {
    tasInterface();
  }
}

void lo0op() {
  tasInterface();
}

void lo0lop() {
  pinMode(PWR, INPUT);
  while (digitalRead(X_PIN)) {
    //pass
  }
  //pinMode(PWR, OUTPUT);
  //digitalWrite(PWR, LOW);
  delay(500);
  //delay(1000);
  //pinMode(PWR, OUTPUT);
  //digitalWrite(PWR, LOW);
  //delay(1000);
}

void batteryPowerOn() {
  pinMode(PWR, INPUT);
  Serial.write("G");
  if (digitalRead(PWR)) {
    while (digitalRead(PWR)) {
      //wait until it drops down
    }
  }
  while (!digitalRead(PWR)) {
    //Waiting until the Power button is pulled up (battery is inserted into console)
    //Serial.write(digitalRead(PWR)+50);
  }
  pinMode(PWR, OUTPUT);
  digitalWrite(PWR, LOW);
  delay(200);
}



byte tasMode = 0;
//tasMode 0 - Standby
//tasMode 1 - Recording
//tasMode 2 - Playback


//expected to toggle only between mode 0/1 and 0/2
//250 toggles back to mode 0
//251 toggles to mode 1
//252 toggles to mode 2
//when going into

/*
   12 buttons on the DSII, possibly a 13th in the future (power)
   2 bytes per frame
   1st bit is byte number (0 is 1st byte, 1 is 2nd byte)
   Next 6 bits are buttons
   Last bit is empty
   Goes in order of the pins list

*/
//12 buttons on the DSII


//Create the FIFO queue
#define queue_size 40 //queue size can't be larger than 255 frames
volatile int in_queue = 0;
#include "queue.h"
QUEUE(buttonbuffer, byte, queue_size * 3);
volatile struct queue_buttonbuffer queue;

volatile boolean poweronstart = false;
volatile boolean restartpower = false;

void tasInterface() {
  //Keeps it in TAS mode until power cycled (reset)
  for (int i = 0; i < Serial.available(); i++) {
    //Checks any incoming bytes
    int incomingbyte = Serial.read();
    //Serial.print("hmm");
    //Serial.print(incomingbyte);
    if (incomingbyte == 51) {
      Serial.print("TAS");
      tasMode = 1;
      //Start tasMode 1
      //Buffer should be cleared
      attachInterrupt(digitalPinToInterrupt(SYNC), tasreadinterrupt, FALLING);
      while (tasMode == 1) {
        //This loop basically should just read from the buffer and send it over serial, the interrupt function does the rest
        //Also it should check if there are any available bytes to read
        byte bufferbyte;
        while (queue_buttonbuffer_pop(&queue, &bufferbyte) == 0) {
          //There's a byte in the queue, it's set to bufferbyte
          //loops until there's no more bytes in the queue
          Serial.write(bufferbyte);
        }
        for (byte i = 0; i < Serial.available(); i++) {
          int incomingbyte = Serial.read();
          Serial.print("Y");
          if (incomingbyte == 50) {
            //Toggle back to mode 0 bit, exit the loop
            tasMode = 0;
          }
        }
      }
      detachInterrupt(digitalPinToInterrupt(SYNC));

      //TAS Mode 1 is done!
    } else if (incomingbyte == 52) {
      //pinMode(A_PIN, OUTPUT);
      //digitalWrite(A_PIN, LOW);
      tasMode = 2;
      in_queue = 0;
      //Start tasMode 2
      //Lets the computer know how big the queue is
      byte queuetosend = queue_size;
      Serial.write(queuetosend);//Telling computer what the queue size is
      //Fill up queue from computer inputs
      while (in_queue < queue_size) {
        for (byte i = 0; i < Serial.available(); i++) {
          byte incomingbyte = Serial.read();
          if (queue_buttonbuffer_push(&queue, &incomingbyte) == 0) {
            //Serial.write(incomingbyte);
            //Serial.print("B");
            if (bitRead(incomingbyte, 0) == 1) {
              //We get a new odd byte (the second of a frame)
              in_queue++;
              Serial.write(in_queue);
            }
          }
          else {
            byte toWrite = 0;
            Serial.write(toWrite);//RED ALERT, QUEUE NOT FUNCTIONING
          }
        }
      }
      //Wait for command from master to start (byte is 52 for starting playing inputs)

      boolean started = false;
      while (started == false) {
        //Loops until replay starts
        for (byte i = 0; i < Serial.available(); i++) {
          byte incomingbyte = Serial.read();
          if (incomingbyte == 52) {
            //Time to start replaying
            started = true;
          }
        }
      }

      byte uselessbyte;
      if (poweronstart) {
        batteryPowerOn();
        while (!digitalRead(X_PIN)) {
          //wait until the x pin is pulled up
        }
        delay(100);
        //poweronstart = false;
        Serial.write("Z");
        ;//remove the first byte from the buffer (which is a poweronbyte)

      }
      //Start replaying
      attachInterrupt(digitalPinToInterrupt(SYNC), taswriteinterrupt, FALLING);
      //Most of the work is done in the interrupt

      if (restartpower) {
        Serial.println("X");
        while (in_queue > 10) {
          //I'm 99% sure that it's redundant, but idc
          //we still have inputs in the buffer
          //tas replay will stop once there are no more frames in the buffer
          if (in_queue < queue_size) {
            //available space in the queue
            for (byte i = 0; i < Serial.available(); i++) {
              byte incomingbyte = Serial.read();
              if (queue_buttonbuffer_push(&queue, &incomingbyte) == 0) {
                if (bitRead(incomingbyte, 0) == 1) {
                  in_queue++;
                }
              }
            }
          }

        }
        detachInterrupt(digitalPinToInterrupt(SYNC));
        byte input;
        for (int i = 0; i < 80; i++) {
          queue_buttonbuffer_push(&queue, &input);
        }
        byte firstin = 126;
        byte secondin = 127;
        while (in_queue < queue_size) {
          queue_buttonbuffer_push(&queue, &firstin);
          queue_buttonbuffer_push(&queue, &secondin);
          in_queue++;

          //fill up the queue with 40 frames of waiting to be ready to power on
        }
        Serial.write(in_queue);
        delay(500);
        pinMode(PWR, OUTPUT);
        digitalWrite(PWR, LOW);
        restartpower = false;
        Serial.write("C");
        delay(500);

        attachInterrupt(digitalPinToInterrupt(SYNC), taswriteinterrupt, FALLING);
      }

      Serial.write("F");

      while (in_queue > 0) {
        //we still have inputs in the buffer
        //tas replay will stop once there are no more frames in the buffer
        if (in_queue < queue_size) {
          //available space in the queue
          for (byte i = 0; i < Serial.available(); i++) {
            byte incomingbyte = Serial.read();
            if (queue_buttonbuffer_push(&queue, &incomingbyte) == 0) {
              if (bitRead(incomingbyte, 0) == 1) {
                in_queue++;
              }
            } else {
              byte toWrite = 0;
              Serial.write(toWrite);//RED ALERT, QUEUE NOT FUNCTIONING
            }
          }
        }

      }

      //queue is empty, TAS replaying is done
      detachInterrupt(digitalPinToInterrupt(SYNC));
      tasMode = 0;
      resetbuttons();
    }else if(incomingbyte == 60){
      poweronstart = true;
      restartpower = true;
    }else if(incomingbyte == 61){
      poweronstart = false;
      restartpower = false;
    }
  }
}



void tasreadinterrupt() {
  //Whenever there's a new frame in read mode
  byte firstByte = 0;
  byte secondByte = 1;
  byte index = 0;
  while (index < 6) {
    bitWrite(firstByte, index + 1, digitalRead(pins[index]));
    index++;
  }
  while (index < 12) {
    bitWrite(secondByte, index - 5, digitalRead(pins[index]));
    index++;
  }
  if (queue_buttonbuffer_push(&queue, &firstByte) == 0) {

  } else {
    Serial.println("Error with queue");
  }
  if (queue_buttonbuffer_push(&queue, &secondByte) == 0) {

  } else {
    Serial.println("Error with queue");
  }
}

void taswriteinterrupt() {
  //Whenever there's a new frame in playback/write mode
  byte firstByte;
  byte secondByte;
  if (queue_buttonbuffer_pop(&queue, &firstByte) == 0) {
    //succesfull
  }
  if (queue_buttonbuffer_pop(&queue, &secondByte) == 0) {
    //succesfull
  }
  //Set all the button states using digitalWrite
  byte index = 0;
  while (index < 6) {
    if (bitRead(firstByte, index + 1)) {
      //HIGH
      pinMode(pins[index], INPUT);
    } else {
      //LOW
      pinMode(pins[index], OUTPUT);
      digitalWrite(pins[index], LOW);
    }
    //digitalWrite(pins[index], bitRead(firstByte, index + 1));
    index++;
  }
  while (index < 12) {
    if (bitRead(secondByte, index - 5)) {
      //HIGH
      pinMode(pins[index], INPUT);
    } else {
      //LOW
      pinMode(pins[index], OUTPUT);
      digitalWrite(pins[index], LOW);
    }
    //digitalWrite(pins[index], bitRead(secondByte, index - 5));
    index++;
  }
  in_queue--;
  pinMode(PWR, INPUT);
  //poweronstart = false;
  //Let the host know how many frames are in the buffer
  Serial.write(in_queue);
  /*
    if (bitRead(secondByte, 7)&&!restartpower) {
    //We're going to do the restart sequence
    restartpower = true;
    detachInterrupt(digitalPinToInterrupt(SYNC));
    Serial.write("A");
    } else if (!restartpower) {
    pinMode(PWR, INPUT);
    //Serial.write("X");
    } else {
    restartpower = false;
    }
  */
}






void checkMode(int incomingbyte) {
  //Checks any incoming bytes to see if they're a mode switching byte
  if (incomingbyte > 49 && incomingbyte < 54) {
    //the byte is telling us to switch modes
    if (mode != incomingbyte - 50) {
      if (incomingbyte - 50 == 2) {
        //means we're switching away from joystick mode
        Joystick.end();
      }
      mode = incomingbyte - 50;
      resetbuttons();
      //means we're switching modes
      if (mode == 2) {
        Joystick.begin();
      }else if(mode==3){
        Serial.write("Z");
      }
    }
  } else if (incomingbyte == 100) {
    //Performs the "handshake test"
    //If it receives byte 100, it will send byte 101 - this is the verification that the desktop program uses to verify that it's an Input Interface connected
    Serial.write(101);
  }
}

void checkModeLoop() {
  for (int i = 0; i < Serial.available(); i++) {
    int incomingbyte = Serial.read();
    checkMode(incomingbyte);
  }
}

void serialInterface() {
  for (int i = 0; i < Serial.available(); i++) {
    //Checks all incoming bytes
    int incomingbyte = Serial.read();
    checkMode(incomingbyte);
    //Serial.write(incomingbyte);
    if (incomingbyte < 25) {
      //Electronically pressing a button
      int buttonnum = incomingbyte - 10;
      pinstatus[buttonnum] = -1;//indicating to the input loop that the button is pressed
      pinMode(pins[buttonnum], OUTPUT);
      digitalWrite(pins[buttonnum], LOW);
    } else {
      //Stopping electronically pressing a button
      int buttonnum = incomingbyte - 30;
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
