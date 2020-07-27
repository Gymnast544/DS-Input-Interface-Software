import math
import pygame, sys
from pygame.locals import *
import serial
from serial.tools import list_ports
import time
import os
import xml.etree.ElementTree as ET
import tkinter as tk
import keyboard
print("Imported all modules")

#####Builtin Input Interface Stuff

display_fps = False
def initViewer():
    global font, clock, size, screen, background
    pygame.init()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    #Setting up the Pygame window
    background = currentskin.backgrounds[selectedbackground.get()]
    size = (background.get_width(), background.get_height())
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("DS Input Viewer")


class Skin:
    """A wrapper class for parsing RetroSpy/NintendoSpy Skins

    Class is able to get attributes and load relevant images into pygame
    by parsing the skin.xml file in all subfolders.
"""
    
    def __init__(self, xmlpath):
        """Initializes a Skin object

Parses the XML file and loads relevant images into pygame.
self.tree gives the full XML tree (if you want to work with that)
self.name, self.author give info about the skin
self.backgrounds and self.buttons are the defining characteristics of the skin"""
        
        self.xmlpath = xmlpath
        tree = ET.parse(xmlpath)
        self.tree = tree#possibly useful in case debugging is wanted
        root = tree.getroot()
        self.rootattribs = root.attrib
        self.name = root.attrib['name']
        self.author = root.attrib['author']
        print(root.attrib)
        self.backgrounds = {}
        self.buttons = {}
        for elem in root:
            if elem.tag=='background':
                #It's a color variant
                background = pygame.image.load(elem.attrib['image'])
                name = elem.attrib['name']
                self.backgrounds[name] =  background
            elif elem.tag=='button':
                name = elem.attrib['name']
                image = pygame.image.load(elem.attrib['image'])
                pos = (int(elem.attrib['x']), int(elem.attrib['y']))
                self.buttons[elem.attrib['name']] = (image, pos)
        

def initSkins():
    """Goes through all subfolders of the skin folder and inits skins

    Goes into 'skins' folder and initializes a skin in every subfolder.
    skins list stores all the skin objects found"""
    
    global skins
    skins = {}
    global cwd
    cwd = os.getcwd()
    os.chdir('skins')
    for folder in os.listdir():
        os.chdir(folder)
        currentskin = Skin('skin.xml')
        skins[currentskin.name]=currentskin
        os.chdir(cwd)
        os.chdir('skins')

lastMouseButton = False
def checkMouseOnButton():
    pos = pygame.mouse.get_pos()
    for name, buttoninfo in currentskin.buttons.items():
        #print(name)
        buttonrect = pygame.Rect(buttoninfo[1], buttoninfo[0].get_rect().size)
        #print(buttonrect)
        if buttonrect.collidepoint(pos):
            return name
        
        #distance = math.sqrt((pos[0]-buttonpos[0])**2+(pos[1]-buttonpos[1])**2)
        #if distance<15:
            #return buttonwpos[0]
    return False

def updateViewer():
    global screen, size
    background = currentskin.backgrounds[selectedbackground.get()]
    screen.blit(background, (0, 0))
    for buttonname in currentbuttons:
        buttoninfo = currentskin.buttons[buttonname]
        screen.blit(buttoninfo[0], buttoninfo[1])
    if display_fps:
        fps = font.render(str(int(clock.get_fps())), True, pygame.Color('white'))
        screen.blit(fps, (0, 0))
    pygame.display.flip()
    clock.tick()

def checkEvents(returnquitdata = False):
    events = pygame.event.get()
    for event in events:
        #print(event)
        if event.type == pygame.locals.QUIT:
            if returnquitdata:
                return -1
        
    return events

#Running mouseInput will allow you to click on buttons on the builtin input display to press them
def mouseInput(events):
    global lastMouseButton
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseonbutton = checkMouseOnButton()
            if mouseonbutton!=False:
                #It's on a button and the mouse is pressed
                sendButton(mouseonbutton)
                lastMouseButton = mouseonbutton
        elif event.type == pygame.MOUSEBUTTONUP:
            if lastMouseButton != False:
                #It's on a button and the mouse is pressed
                releaseButton(lastMouseButton)
                lastMouseButton = False

#When using the builtin input display if you press a button and run keyboardInput it'll press the buttons you pressed
pygamekeystobuttonsdict = {pygame.K_a:"a", pygame.K_b:"b", pygame.K_x:"x", pygame.K_y:"y", pygame.K_LEFT:"left", pygame.K_RIGHT:"right", pygame.K_UP:"up", pygame.K_DOWN:"down", pygame.K_l:"l", pygame.K_r:"r", pygame.K_LCTRL:"start", pygame.K_RCTRL:"select"}
def keyboardInputPygame(events):
    for event in events:
        if event.type == pygame.KEYDOWN:
            if pygamekeystobuttonsdict.get(event.key)!=None:
                #valid key
                sendButton(pygamekeystobuttonsdict[event.key])
        elif event.type == pygame.KEYUP:
            if pygamekeystobuttonsdict.get(event.key)!=None:
                #valid key
                releaseButton(pygamekeystobuttonsdict[event.key])

keyboardcontrolregvar = False
keystobuttonsdict = {"a":"a", "b":"b", "x":"x", "y":"y", "left":"left", "right":"right", "up":"up", "down":"down", "l":"l", "r":"r", "ctrl":"start", "right ctrl":"select"}
#ctrl is left ctrl
def updatekeebcontrol():
    global keyboardcontrolregvar, keyboardcontrol
    keyboardcontrolregvar = keyboardcontrol.get()
    #print("Keyboard control updated")
def keyboardInput(keyevent):
    global keyboardcontrol
    if keyboardcontrolregvar== True:
        if keyevent.event_type == "down":
            if keystobuttonsdict.get(keyevent.name)!=None:
                #valid key
                sendButton(keystobuttonsdict[keyevent.name])
        elif keyevent.event_type == "up":
            if keystobuttonsdict.get(keyevent.name)!=None:
                #valid key
                releaseButton(keystobuttonsdict[keyevent.name])
hook = keyboard.hook(keyboardInput)
print("Inited keyboard hook")





####Serial Stuff

def chooseDevice():
    serialdevices = []
    for index, serialport in enumerate(list_ports.comports()):
        print(str(index+1)+": "+serialport.description)
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

"""
SERIAL PROTOCOL
10-21 are down A, B, X, Y, DL, DR, DU, DD, L, R, ST, SE
30-41 are up A, B, X, Y, DL, DR, DU, DD, L, R, ST, SE 
sending a button down char to the arduino will electronically press that button
sending a button up char to the arduino will switch that button to input (releasing the button)
"""

chartobuttondict = {10:"a", 11:"b", 12:"x", 13:"y", 14:"left", 15:"right", 16:"up", 17:"down", 18:"l", 19:"r", 20:"start", 21:"select"}
buttontochardict = {v: k for k, v in chartobuttondict.items()}
currentbuttons = []

def getInputs():
    global currentbuttons
    buttons = []
    #only updates if there's something to read
    if ser.in_waiting>0:
        buttons = ser.read(ser.in_waiting)
    for x in buttons:
        try:
            if x>28:
                buttonstate = False
                buttonName = chartobuttondict[x-20]
                #print(buttonName)
            else:
                buttonstate = True
                buttonName = chartobuttondict[x]
            if buttonstate == True:
                #button has been pressed
                if not buttonName in currentbuttons:
                    currentbuttons.append(buttonName)
            else:
                #button has been released
                currentbuttons.remove(buttonName)

        except:
            print("error with ", x)

def sendByte(byteint):
    global ser
    ser.write(bytes(chr(byteint), 'utf-8'))


def sendButton(buttonName):
    global currentbuttons, ser
    if not(buttonName in currentbuttons):
        currentbuttons.append(buttonName)
    sendByte(buttontochardict[buttonName])

def releaseButton(buttonName):
    global currentbuttons, ser
    try:
        currentbuttons.remove(buttonName)
    except:
        print("error removing button name from list")
    sendByte(buttontochardict[buttonName]+20)#sends the button to be digitally released


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


def listDevicesGUI(verify):
    ##Returns a dict with the available serial devices
    ##verifys devices if applicable
    serialdevices = {}
    for serialport in list_ports.comports():
        print("Checking "+str(serialport))
        if verify:
            if verifyDevice(serialport.device):
                serialdevices[serialport.description]=serialport.device
        else:
            serialdevices[serialport.description]=serialport.device
    return serialdevices
    
    
 


comportdict = {}
verifydevices = True
def updatecomportdict():
    global comportdict
    comportdict=listDevicesGUI(verifydevices)

def initvars():
    global inputdisplaythread
    pygame.init()
    print("Inited pygame")
    updatecomportdict()
    print("Updated comports")
    initSkins()
    print("Inited Skins")
    #inputdisplaythread = threading.Thread(target=launchInputDisplay)


comportbuttons = []
def connectSerial():
    print(currentcomport.get())
    initSerial(currentcomport.get())
    for button in comportbuttons:
        button['state'] = 'disabled'
    for button in modebuttons:
        button['state']='normal'
    comportconnectbutton['state'] = 'disabled'
    comportdisconnectbutton['state']='normal'
    changeMode()
    
def endSerial():
    closeSerial()
    for button in comportbuttons:
        button['state'] = 'normal'
    for button in modebuttons+inputdisplayoptionsbuttons:
        button['state']='disabled'
    comportdisconnectbutton['state'] = 'disabled'
    comportconnectbutton['state']='normal'
        
def changeMode():
    sendByte(int(interfacemode.get())+50)
    print("Changed mode to: ",interfacemode.get())
    if interfacemode.get()==0:
        newstate = 'normal'
    else:
        newstate = 'disabled'
        
    for button in inputdisplayoptionsbuttons:
        button['state'] = newstate


inputdisplayrunning = False

def launchInputDisplay():
    global inputdisplayrunning
    inputdisplayrunning = True
    initViewer()


def runInputDisplay():
    getInputs()
    events = checkEvents(returnquitdata=True)
    if events==-1:
        inputdisplayrunning=False
        pygame.quit()
        sys.exit()
    else:
        if mousecontrol.get():
            mouseInput(events)
        elif keyboardcontrol.get():
            pass
            #keyboardInput(events)
        updateViewer()

def updateSkinInfo(name):
    global currentskin, currentskinauthor, backgrounds, authorlabel, inputdisplaythread
    currentskin = skins[name]
    currentskinauthor = currentskin.author
    authorlabel['text'] = "Author: "+currentskinauthor
    backgrounds = list(currentskin.backgrounds.keys())

    if inputdisplayrunning:
        #updating screen size, though if pygame isn't running this will crash?
        global size
        size = (background.get_width(), background.get_height())
        screen = pygame.display.set_mode(size)
    
    #Updates the background select dropdown with new options
    selectedbackground.set(backgrounds[0])
    BackgroundSelectDropdown['menu'].delete(0, 'end')
    for color in backgrounds:
       BackgroundSelectDropdown['menu'].add_command(label=color, command=tk._setit( selectedbackground, color))
    

def updateBackgroundInfo(name):
    pass
    

def tKinter():
    window = tk.Tk()
    print("Created TK window")
    window.title("DS Input Interface Command Center")
    #title = tk.Label(master=window, text="DS Input Interface")
    #title.pack()
    
    portselectframe = tk.Frame(master=window)
    portselectframe.pack()

    portselectlabel = tk.Label(master = portselectframe, text = "Select the USB device of the DS Input Interface that you want to work with.")
    portselectlabel.pack()
    currow=1
    #portselectbuttonframe = tk.Frame(master=portselectframe)
    global currentcomport
    currentcomport = tk.StringVar()
    #ports = {"this is a big port 1":"port 1", "this is a big port 2":"port 2","this is a big port 3":"port 3"}
    global comportbuttons
    for longname, shortname in comportdict.items():
        radiobutton = tk.Radiobutton(master=portselectframe, text=longname, variable=currentcomport, value=shortname)
        #radiobutton.grid(row=currow)
        #currow+=1
        radiobutton.pack(side=tk.TOP)
        radiobutton.select()
        comportbuttons.append(radiobutton)
    comportselectbuttonframe = tk.Frame(master=window)
    comportselectbuttonframe.pack(side=tk.TOP)

    global comportconnectbutton
    comportconnectbutton = tk.Button(master=comportselectbuttonframe, text="Connect to Serial Port", command=connectSerial)
    comportconnectbutton.pack(side=tk.LEFT)
    
    global comportdisconnectbutton
    comportdisconnectbutton = tk.Button(master=comportselectbuttonframe, text="Disconnect from Serial Port", command=endSerial, state='disabled')
    comportdisconnectbutton.pack(side=tk.LEFT)

    modeselectframe = tk.Frame(master=window)
    modeselectframe.pack()
    tk.Label(master=modeselectframe, text = "Select the mode of the DS Input Interface").pack()

    global interfacemode
    interfacemode = tk.IntVar()

    global modebuttons
    modebuttons = []
    numModes = 3
    for index in range(numModes):
        radiobutton = tk.Radiobutton(master=modeselectframe, text="Mode "+str(index+1), variable=interfacemode, value=index, command=changeMode, state='disabled')
        radiobutton.pack(side=tk.TOP)
        if index==0:
            radiobutton.select()
        modebuttons.append(radiobutton)

    modeoneoptionsframe = tk.Frame(master=window)
    modeoneoptionsframe.pack()

    
    global mousecontrol
    mousecontrol = tk.BooleanVar()
    global keyboardcontrol
    keyboardcontrol = tk.BooleanVar()
    #global controllerpassthrough
    #controllerpassthrough= tk.BooleanVar()
    global selectedskin
    selectedskin = tk.StringVar()
    global selectedbackground
    selectedbackground = tk.StringVar()

    mouseControlButton = tk.Checkbutton(master=modeoneoptionsframe, text="Mouse control", variable=mousecontrol, state='disabled')
    mouseControlButton.pack()

    keyboardControlButton = tk.Checkbutton(master=modeoneoptionsframe, text="Keyboard control", variable=keyboardcontrol, state='disabled')
    keyboardControlButton.pack()

    #controllerPassthroughButton = tk.Checkbutton(master=modeoneoptionsframe, text="Controller passthrough", variable=controllerpassthrough, state='disabled')
    #controllerPassthroughButton.pack()



    inputdisplayskinsframe = tk.Frame(master=modeoneoptionsframe)
    inputdisplayskinsframe.pack()
    
    SkinSelectDropdown = tk.OptionMenu(inputdisplayskinsframe, selectedskin, *list(skins.keys()), command=updateSkinInfo)
    SkinSelectDropdown.pack(side=tk.LEFT)
    selectedskin.set(list(skins.keys())[0])
    backgrounds = list(skins[selectedskin.get()].backgrounds.keys())
    global currentskin
    currentskin = skins[selectedskin.get()]

    global BackgroundSelectDropdown
    BackgroundSelectDropdown = tk.OptionMenu(inputdisplayskinsframe, selectedbackground, *backgrounds, command=updateBackgroundInfo)
    BackgroundSelectDropdown.pack(side=tk.LEFT)
    selectedbackground.set(backgrounds[0])

    global authorlabel
    authorlabel = tk.Label(master=modeoneoptionsframe, text="Author: "+currentskin.author)
    authorlabel.pack()

    
    

    inputDisplayLaunchButton = tk.Button(master=modeoneoptionsframe, text = "Launch Input Display", command=launchInputDisplay, state='disabled')
    inputDisplayLaunchButton.pack()

    

    global inputdisplayoptionsbuttons
    inputdisplayoptionsbuttons = [mouseControlButton, keyboardControlButton, inputDisplayLaunchButton, SkinSelectDropdown, BackgroundSelectDropdown]#Note omission of controllerPassthroughButton

    print("Started loop")
    while True:
        window.update()
        if inputdisplayrunning:
            runInputDisplay()
            updatekeebcontrol()
    



if __name__ == "__main__":
    print("Started main")
    initvars()
    print("Finished initing vars")
    tKinter()














