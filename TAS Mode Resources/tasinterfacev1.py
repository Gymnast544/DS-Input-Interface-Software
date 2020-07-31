import serial
from serial.tools import list_ports
import time

#No GUI for this right now, maybe in the future
#This program takes a text file of bytes and sends them to the Input Interface following the custom serial protocol written
#to get the text file, use dsmtobytes.py


filename = "openingmenu.txt" #this is the name of the file that inputs are sent to


def chooseDevice():
    serialdevices = []
    for index, serialport in enumerate(list_ports.comports()):
        print(str(index+1)+": "+serialport.description+" Verified: "+str(verifyDevice(serialport.device)))
        serialdevices.append(serialport.device)
    serialindex = int(input("Choose the serial port to use (Enter the number) "))
    comport = serialdevices[serialindex-1]
    return comport

ser = None
def initSerial(comport):
    global ser
    ser = serial.Serial(comport)
    ser.baudrate = 115200

def closeSerial():
    global ser
    ser.close()

def sendByte(byteint):
    global ser
    ser.write(bytes(chr(byteint), 'utf-8'))
def verifyDevice(comport):
    verified = False
    tempser = serial.Serial(comport)
    tempser.baudrate = 115200
    tempser.write(bytes(chr(100), 'utf-8'))
    starttime = time.time()
    while time.time()-starttime<.5 and verified==False:
        if tempser.in_waiting>0:
            read = tempser.read(1)
            if ord(read)==101:
                verified = True
                tempser.close()
                return True
    tempser.close()
    print("Verification status of "+comport+" is "+str(verified))
    return verified



initSerial(chooseDevice())
time.sleep(.1)
sendByte(53)#switches to TAS mode
time.sleep(.2)
incomingBytes = ser.read(ser.in_waiting)
for inp in incomingBytes:
    print(inp)
print("Drained bytes")
#Drains inputs, in case theres something in the serial buffer

#this loop just drains all the pending bytes
f = open(filename, "r")
#reads just the first line of the file and then closes it
if "128" in f.readline():
    #this means that we're booting on battery start and restarting the DS later
    print("Powering on and restarting")
    sendByte(60)#60 is the byte indicator for this
else:
    sendByte(61)#this just verifies that the variables are off
f.close()



sendByte(52)#this tells the DS that we're ready to go into TAS playback mode
time.sleep(.1)
incomingBytes = []
if ser.in_waiting>0:
        incomingBytes = ser.read(ser.in_waiting)
for incomingByte in incomingBytes:
    queuesize = int(str(incomingByte))
    print("Queue size:", queuesize)

f = open(filename, "r")
in_queue = 0
while in_queue<queuesize:
    #This loop is filling up the queue
    #It sends two bytes (1 frame worth of data)
    #it receives the number of frames in queue
    #Runs until the queue is filled
    firstByte = int(f.readline().strip())
    if firstByte==128:
        sendByte(int(f.readline().strip()))
        sendByte(int(f.readline().strip()))
    else:
        sendByte(firstByte)
        sendByte(int(f.readline().strip()))
    print("sent bytes")
    while ser.in_waiting<=0:
        pass
    incomingBytes = ser.read(ser.in_waiting)
    for byte in incomingBytes:
        print(byte, chr(byte))
        in_queue = int(str(byte))
        #print(in_queue)
    print("In queue: ", in_queue)


#Queue is filled
#Pro Micro is waiting for the command to start
print("Queue filled")
input("Press enter to start")
sendByte(52)#this byte tells the Pro Micro to start playing back inputs (or waiting for the battery to be inserted)
starttime = time.time()
numsent = 0
running = True
while running:
    while ser.in_waiting<=0:
        pass
    incomingBytes = ser.read(ser.in_waiting)
    for byte in incomingBytes:
        print(byte, chr(byte)) #prints every incoming byte, as well as it's ASCII character
        in_queue = int(str(byte))
        #print(in_queue)
    for i in range((queuesize-in_queue)):
        try:
            #reads the first two bytes
            byte1 = int(f.readline().strip())
            byte2 = int(f.readline().strip())
            if byte2 == 255:
                #this indicates a restart cycle in the TAS (put a 255 after the last A press)
                waiting = True
                print("Waiting")
                while waiting:
                    #waits until it receives a byte of 70 from the DS (restart successful)
                    while ser.in_waiting<=0:
                        pass
                    incomingbytes = ser.read()
                    for byte in incomingbytes:
                        print(byte)
                        if byte == 70:
                            #time to break out of this
                            waiting = False
            else:
                sendByte(byte1)
                sendByte(byte2)
            numsent+=1
        except:
            running = False
            print("Error sending byte")
        #Sends number of bytes as frames in queue
            
#this gives the average FPS. Not super useful when doing restart cycles, but can help during debuggin
print((numsent/(time.time()-starttime))/2) 


"""

This here is the code I used to try to record inputs
Due to software limitations, it desyncs easily from the console
It's here if anyone wants to mess around with it, but it's not
something that should work

sendByte(51)

#f = open("recording.txt", "w")
running = True
print("Started")
while running:
    incomingBytes = []
    if ser.in_waiting>0:
        incomingBytes = ser.read(ser.in_waiting)
    for incomingByte in incomingBytes:
        #f.write(str(incomingByte)+"\n")
        print(incomingByte)
        if str(incomingByte) == "118":
            running = False

sendByte(50)
f.close()
"""

