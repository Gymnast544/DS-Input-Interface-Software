import socket
import threading
from ahk import AHK
"""
Written by StreamersVsChat and modified by Gymnast544
This video was used to code this https://youtu.be/uE_3RRBz3CQ - take a look at it to fill out the required fields
Configured for the DS Input Interface

Set up the Input Interface normally, with an input display
Enable Keyboard Control of the Input Interface
This program presses keys using AHK, and communication is done via keypresses



"""


#Download Autohotkey at https://www.autohotkey.com/ and provide the address to
#AutoHotkey.exe below!
ahk = AHK(executable_path='C:\Program Files\AutoHotkey\AutoHotkey.exe')

SERVER = "irc.twitch.tv"
PORT = 6667

#Your OAUTH Code Here https://twitchapps.com/tmi/
PASS = ""

#What you'd like to name your bot
BOT = "TwitchPlaysTestBot"

#The channel you want to monitor
CHANNEL = "gymnast544"

#Your account
OWNER = "Gymnast544"

message = ""
user = ""

irc = socket.socket()

irc.connect((SERVER, PORT))
irc.send((	"PASS " + PASS + "\n" +
			"NICK " + BOT + "\n" +
			"JOIN #" + CHANNEL + "\n").encode())

def gamecontrol():

	global message

	while True:

		if "up" == message.lower():
			ahk.key_press('up')
			message = ""

		if "down" == message.lower():
			ahk.key_press('down')
			message = ""

		if "left" == message.lower():
			ahk.key_press('left')
			message = ""

		if "right" == message.lower():
			ahk.key_press('right')
			message = ""

		if "a" == message.lower():
			ahk.key_press('a')
			message = ""

		if "b" == message.lower():
			ahk.key_press('b')
			message = ""

		if "x" == message.lower():
			ahk.key_press('x')
			message = ""

		if "y" == message.lower():
			ahk.key_press('y')
			message = ""

		if "l" == message.lower():
			ahk.key_press('l')
			message = ""

		if "r" == message.lower():
			ahk.key_press('r')
			message = ""

def twitch():

	global user
	global message

	def joinchat():
		Loading = True
		while Loading:
			readbuffer_join = irc.recv(1024)
			readbuffer_join = readbuffer_join.decode()
			print(readbuffer_join)
			for line in readbuffer_join.split("\n")[0:-1]:
				print(line)
				Loading = loadingComplete(line)

	def loadingComplete(line):
		if("End of /NAMES list" in line):
			print("TwitchBot has joined " + CHANNEL + "'s Channel!")
			sendMessage(irc, "Hello World!")
			return False
		else:
			return True

	def sendMessage(irc, message):
		messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
		irc.send((messageTemp + "\n").encode())

	def getUser(line):
		#global user
		colons = line.count(":")
		colonless = colons-1
		separate = line.split(":", colons)
		user = separate[colonless].split("!", 1)[0]
		return user

	def getMessage(line):
		#global message
		try:
			colons = line.count(":")
			message = (line.split(":", colons))[colons]
		except:
			message = ""
		return message

	def console(line):
		if "PRIVMSG" in line:
			return False
		else:
			return True

	joinchat()
	irc.send("CAP REQ :twitch.tv/tags\r\n".encode())
	while True:
		try:
			readbuffer = irc.recv(1024).decode()
		except:
			readbuffer = ""
		for line in readbuffer.split("\r\n"):
			if line == "":
				continue
			if "PING :tmi.twitch.tv" in line:
				print(line)
				msgg = "PONG :tmi.twitch.tv\r\n".encode()
				irc.send(msgg)
				print(msgg)
				continue
			else:
				try:
					user = getUser(line)
					message = getMessage(line)
					print(user + " : " + message)
				except Exception:
					pass

def main():
	if __name__ =='__main__':
		t1 = threading.Thread(target = twitch)
		t1.start()
		t2 = threading.Thread(target = gamecontrol)
		t2. start()
main()
