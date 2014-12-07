"""
Zaber.py
Brian Perrett
12/07/14

A large edit of Mach1.py
Separates the usage of the zaber stage into its own class
"""

from __future__ import division
import serial, struct, time, glob, sys


class Zaber():
	# static variables
	cmd = {
	"home": 1, 
	"moveAbsolute": 20, 
	"moveRelative": 21,
	"setTargetSpeed": 42,
	"storeCurrentPosition": 16,
	"returnStoredPosition": 17,
	"moveToStoredPosition": 18,
	"returnStatus": 54
	}

	translation = {"both": 0, "hor": 1, "ver": 2}
	# microstep in mm
	microstep = 0.00009921875

	def __init__(self, zaberStagePort = 2):
		"""
		initialize variables.
		zaberStagePort 	- Port for zaber stage.  2 by default.  Could be 0 or 1.
		"""
		# Serial() input depends on where stage is connected
		self.stage = serial.Serial(zaberStagePort)

	def zaberReceive(self):
		# return 6 bytes from the receive buffer
		# there must be 6 bytes to receive (no error checking)
		r = [0,0,0,0,0,0]
		for i in range (6):
			r[i] = ord(self.stage.read(1))
			return r

	def zaberSend(self, device, command, data=0):
		"""
		Generally not used by user.
			used by all zaber functions to send commands to the zaber stage.
			send a packet using the specified device number, command number, and data
			The data argument is optional and defaults to zero (really shouldn't be optional though, you kind of need it)
		device - "hor" or "ver"
		"""
		packet = struct.pack('<BBl', self.translation[device], command, data)
		self.stage.write(packet)
		r = self.zaberReceive()
		return r
		
	def storeLocation(self, stage, address):
		"""
		stores location data at given address in the zaber stage.
		__Variables__
		stage 	- hor or ver
		address - number 0-15
		"""
		self.zaberSend(stage, self.cmd["storeCurrentPosition"], address)

	def moveToStoredLocation(self, stage, address):
		"""
		Moves to stored location at given address in the zaber stage.
		__Variables__
		stage 	- hor or ver
		address - number 0-15
		"""
		self.zaberSend(stage, self.cmd["moveToStoredPosition"], address)

	def convertDistance(self, mm):
		"""
		Generally not used by user.
			Used internally by zaber movement methods.
			converts mm to microsteps
		__Variables__
		mm - millimeters 
		"""
		return mm/(self.microstep)
		
	def convertSpeed(self, v):
		"""
		Generally not used by user.
			used by internal setSpeed method
			Converts v to units that make sense to stage and returns converted
		__Variables__
		v - in mm/s
		"""
		converted = v/(self.microstep*9.375)
		return converted

	def move(self, stage, command, data):
		"""
		Moves horizontal or vertical translation stage data mm.
		__Variables__
		stage 	- "hor" or "ver"
		command - one of the movement commands from the cmd dictionary.
		data 	- a distance in mm.
		"""
		dist = self.convertDistance(data)
		r = self.zaberSend(stage, command, dist)
		return r
		
	def setSpeed(self, v):
		"""
		Sets both translation stage speeds
		__Variables__
		v - speed to set in mm
			converts to numbers that the stage wants and calls a command in the cmd dictionary
		"""
		converted = self.convertSpeed(v)
		print(converted)
		# set both stage speeds
		self.zaberSend(self.translation["hor"], self.cmd["setTargetSpeed"], data = converted)
		self.zaberSend(self.translation["ver"], self.cmd["setTargetSpeed"], data = converted)

	def wait(self):
		"""
		__UNTESTED__

		stops program until both stages return idle statuses
		"""
		while True:
			r1 = self.zaberSend(self.translation["hor"], self.cmd["returnStatus"], data=0)
			r2 = self.zaberSend(self.translation["ver"], self.cmd["returnStatus"], data=0)
			if r1[2] == 0 and r2[2] == 0:
				break
			else:
				time.sleep(.01)