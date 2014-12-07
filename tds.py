"""
tds.py
Brian Perrett
12/07/14
Used largely as a wrapper for the pytek library to control the tds2014 oscilloscope
__dependencies__
	python 2.7
	pyserial
	pytek
"""

from __future__ import division
import serial, struct, time, glob, sys
from pytek import TDS3k


class Tds():

	def __init__(self, oscPort = "COM1"):
		"""
		initialize variables.
		oscPort - Port for oscilloscope.  COM1 by default.  Could be COM2 or 3 as well.
		"""
		# 9600 = baudrate
		self.osc = TDS3k(serial.Serial(oscPort, 9600, timeout=1))

	def getSingleMeasurement(self, ch = "CH1"):
		"""
			input which channel you want data from.
		returns y value from get_waveform() aka Voltage Reading from oscilloscope
		__Variables__
		ch - "CH1" or "CH2"
		"""
		counter = 1
		# added try except block to take care of times when get_waveform() has a problem.
		# this seems to take a long time.  Calling for data from oscilloscope is slow... May need to
		#     Take many samples at once, receive data all at once.
		while True:
			try:		
				waveform = self.osc.get_waveform(source = ch, start = 0, stop = 0)
				break
			except:
				print("Retry: " + str(counter))
				counter += 1
		for x,y in waveform:
			voltage = y
		return voltage

	def getAvgOfSamples(self, ch = "CH1", samples = 100):
		"""
		gets a continuous stream of <samples> samples, and then get their average and return a single value.
		__Variables__
			ch		- which channel you want to take the measurement from.  Defaults to CH1
			samples - Number of samples you would like to average
		"""
		self.isReady()
		counter = 1
		while True:
			try:		
				waveform = self.osc.get_waveform(source = ch, start = 1, stop = samples)
				break
			except:
				print("Retry: " + str(counter))
				counter += 1
		y_array = []
		for x,y in waveform:
			y_array.append(y)
		voltage = sum(y_array)/len(y_array)
		return voltage

	def getWaveform(self, ch="CH1", samples=2500):
		"""
		return waveform value list
		"""
		self.isReady()
		counter = 1
		while True:
			try:		
				waveform = self.osc.get_waveform(source = ch, start = 1, stop = samples)
				break
			except:
				print("Retry: " + str(counter))
				counter += 1
		y_array = []
		for x,y in waveform:
			y_array.append(y)
		return y_array

	def setAquireState(self, arg):
		"""
		sends ACQuire:STATE command to tektronix oscilloscope
		Manual says this is equivalent to hitting the RUN/STOP button.
		__Variables__
		String arg - { OFF | ON | RUN | STOP | <NR1> }
		"""
		self.osc.send_command("ACQ:STATE", arg)

	def setStopAfter(self, arg):
		"""
		sends ACQuire:STOPAfter command to tektronix oscilloscope
		__Variables__
		String arg - { RUNSTop | SEQuence }
		"""
		self.osc.send_command("ACQ:STOPA", arg)

	def setSecDiv(self, arg):
		"""
		__Variables__
		String arg - some number of seconds
			inputting "2" sets the divisions to 2.5 seconds.
		"""
		valid = ["1", "2", "5", "10"]
		self.osc.send_command("HOR:MAI:SCA", arg)

	def trigger(self):
		"""
		puts into ready, single sequence mode, then	forces a trigger.
		"""
		self.setAquireState("RUN")
		self.setStopAfter("SEQ")
		self.osc.trigger()

	def isReady(self):
		"""
		waits for the oscilloscope to be done taking measurements before returning True.
		
		perhaps not a good method name.  The oscilloscope will end in
			"acquisition done" mode and not "ready"
		"""
		while self.osc.trigger_state() != "save":
			time.sleep(.1)
		return True