"""
This program converts "DSM" files to TXT files which can be sent to the Input Interface in TAS mode
It can't understand the headers of a DSM file, so there's the startline and endline variables which allow you to start directly after it
An empty line in the text file (Just a newline character) counts as a frame with no input
The way this program works is it looks for upper-case characters corresponding to each button in each line

lowercase characters and most special characters (including "//", "#", and "-") are ignored if put after the content of the line (be sure to separate it from the content with at least a " ")
This means you can comment your TASes if you want to
Example can be seen in the openingmenu.dsm file


This means that a line which is:
|0|.............000 000 0|
Is equivalent to a blank line according to this program

A line like this:
|0|.......A.....000 000 0|
Is equivalent to simply:
A

A line like this:
|0|R.....B.Y....000 000 0|
Is equivalent to simply:
RBY
or
BRY

Button characters:
RLDUTSBAYXWE (Right,Left,Down,Up,sTart,Select,B,A,Y,X,lshoulder,rshoulder)
(W is left shoulder, E is right shoulder, modeled after west and east)

(The order doesn't matter)

This makes it fairly easy to write TASes and modify existing ones, as you don't need to worry about the brackets and special characters
In Desmume, the loads are faster than what is actually on DS console.
If you're console verifying runs, you'll find that you want to insert a lot of empty frames with no inputs
There are also some other things I found myself wanting to do, so this program is able to parse a few custom commands

DELAY command
Inserts a number of frames with no input
line is "DELAY #"
# is number of frames

LOOP command
Rapid-fire button presses a number of times
line is "LOOP buttons #"
buttons is what buttons you want to be pressed (ABXYUDLRWE etc)
# is number of times
It takes 2 times the number of frames as # (alternates between the buttons being pressed and an empty frame)
The first frame has the buttons pressed, second has them not pressed, third pressed, fourth not pressed, etc.
This was useful in choosing the date/time/year in setup, where there are a lot of rapid-fire press-and-release inputs

BATTERYPOWERON command
there should be nothing else on the line other than "BATTERYPOWERON"
This must be the first line of the DSM file if used (if put later, it will mess up the output)
This command puts the input interface into power functions mode
If this command is used:
Input Interface will auto-power on when battery is inserted
Input Interface will auto-restart after the PWR command (given that the DS is turning off on its own, which is one use case - the openingmenu/setup)

PWR command
there should be nothing else on the line other than "BATTERYPOWERON"
sends the bytes 126 and 255 to the Arduino
This indicates that it's restarting.
See the example openingmenu file for the use case of this
It will not work unless the Arduino is set to power functions mode

If you want to combine two DSM files (for example, use the same setup file but then have a different game TAS):
Run this program for each one individually
Copy the output of the second file to directly after the output of the other file
Make sure there are no empty lines in between them


startline variable is inclusive
endline variable is inclusive
If you want it to go to the end of the DSM file, just make the endline variable very large (like a few billion or something), it'll stop at the end of the file

Set the correct file input and output names - output file will be automatically created, doesn't need to exist already

Feel free to copy and modify openingmenu.dsm to work for you - it's somewhat well commented so you can understand what's going on
"""
startline = 1 #inclusive
endline = 100000 #inclusive


f = open("openingmenu.dsm", "r")#DSM file to read from
g = open("openingmenu.txt", "w")#Output file


byte1buttons = ["A", "B", "X", "Y", "L", "R"]
byte2buttons = ["U", "D", "W", "E", "T", "S"]




def parseLine(line, send=True):
    byte1 = 0
    byte2 = 1
    for (i, j) in enumerate(byte1buttons):
        if not(j in line):
            #this button is being pressed
            byte1+=2**(i+1)
        else:
            #print(j)
            pass
    for (i, j) in enumerate(byte2buttons):
        if not(j in line):
            #this button is being pressed
            byte2+=2**(i+1)
    if "PWR" in line:
        byte1 = 126
        byte2 = 255
        print("POWER")
    #print(byte1, byte2)
    if send == True:
        g.write(str(byte1)+"\n"+str(byte2)+"\n")
    else:
        return [byte1, byte2]

for i in range(startline-1):
    f.readline()

for i in range(endline-startline+1):
    line = f.readline()
    #print(line)
    if "DELAY" in line:
        numframes = line[6:].strip()
        byte1=126
        byte2=127
        for i in range(int(numframes)):
            g.write(str(byte1)+"\n"+str(byte2)+"\n")
    elif "LOOP" in line:
        splitline = line.split(" ")
        command = splitline[1]
        numtimes = splitline[2]
        for i in range(int(numtimes)):
            parseLine(command)
            parseLine(" ")
    elif "BATTERYPOWERON" in line:
        g.write("128\n")
    elif line != "":
        parseLine(line)
    else:
        #empty line - file is done
        g.close()
        break
    

print("Finished")

g.close()
