For setting up the Arduino software:
The windows store app works, though the exe distribution from the Arduino site should work. I'm not sure about the Arduino Create online IDE, but I don't think it'll work.

Add the Joystick Library:
https://github.com/MHeironimus/ArduinoJoystickLibrary/tree/version-2.0

Add the Pro Micro board/drivers:
https://learn.sparkfun.com/tutorials/pro-micro--fio-v3-hookup-guide/all

Plug in the Pro Micro
Select the Port
Change the board type from 3V/8Mhz to 5V/16Mhz - IMPORTANT - you can "brick" your Pro Micro board if you forget to do this, and it's really easy to overlook

You should be able to program the Pro Micro board. DS Driver Master is the program that v1 Input Interface boards shipped with, and it will work with v1.2 boards.

V1.2 boards shipped with the ds_tas_master code, which includes all code from the DS Driver Master with an additional TAS mode. Note: TAS mode will not work unless you solder the additional two wires (See hardware setup guide).

I (Gymnast544) am not liable if you brick your Pro Micro board.

Reviving bricked Pro Micro boards - https://learn.sparkfun.com/tutorials/pro-micro--fio-v3-hookup-guide/all#ts-revive