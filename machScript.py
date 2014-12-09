"""
machScript.py
Brian Perrett
December 7, 2014

Uses zaber.py and tds.py to take measurements on an optic.
"""

from __future__ import division
from zaber import Zaber
from tds import Tds
import os.path
import time
import numpy as np

global numScans
# relevant variables
print("setting variables")
opticDiameter = int(raw_input("Diameter of the optic (mm): "))
print("optic diameter = " + str(opticDiameter) + " mm.")
numScans = int(raw_input("# vertical scans: ")) # number of scans to do across the optic
print("# Vertical Scans = " + str(numScans) + ".")
dx = float(opticDiameter) / float(numScans)  # mm distance to move horizontally each time a scan finishes
print("Will move " + str(dx) + "mm each transition.")

print("zaber = Zaber stage object")
zaber = Zaber(zaberStagePort=2)
print("tds = Tds oscilloscope object")
tds = Tds(oscPort="COM1")
print("Setting seconds/div to 2.5")
tds.setSecDiv("2")

# print("setting speed...")
# dev.setSpeed(2) # mm/s

x = []  # x-position
y = []  # y-position
v1 = []  # voltage ch1
v2 = []  # voltage ch2

# dev.zaberStoreLocation(dev.translation["hor"], 14)
# dev.zaberStoreLocation(dev.translation["ver"], 15)

# global variables
global x_loc, _cal1, _cal2
x_loc = 0

def snake(dx, zaber, tds):
	"""
	does a single vertical scan, moves over dx, does another vertical scan, ends at new position
	returns x, y, v1, v2 for first scan and then reversed x_2, y_2, v1_2, v2_2 of second scan
	"""
	# Storing locations seems finicky...
	# print("storing locations...")
	# dev.zaberStoreLocation("hor", 1)
	# dev.zaberStoreLocation("ver", 2) #different address just in case stage combines memory or something
	global x_loc

	x_array = []
	y_array = []
	v1 = []
	v2 = []
	
	# MOVE UP
	#############################################
	x_temp, y_temp, v1_temp, v2_temp = move_up()
	x_array.append(x_temp)
	y_array.append(y_temp)
	v1.append(v1_temp)
	v2.append(v2_temp)
	#############################################

	#  move horizontal
	print("Moving horizontal " + str(dx) + "mm.")
	zaber.move("hor", command="moveRelative", data=dx)
	# time.sleep(10)
	x_loc += dx
	time.sleep(.5)

	# MOVE DOWN
	#############################################
	x_temp, y_temp, v1_temp, v2_temp = move_down()
	x_array.append(x_temp)
	y_array.append(y_temp)
	v1.append(v1_temp)
	v2.append(v2_temp)
	#############################################

	#  move horizontal
	print("moving horizontal " + str(dx) + "mm.")
	zaber.move("hor", command="moveRelative", data=dx)
	x_loc += dx

	return x_array, y_array, v1, v2

def move_up():
	"""
	Moves up the diameter of optic and takes a continuous measurement while moving.
		Moves past the end by 
	returns x array, y array, v array
	"""
	global opticDiameter, x_loc, _cal1, _cal2
	x_array = [x_loc]*2500
	y_array = list(np.linspace(0, opticDiameter, 2500))

	if x_loc == 0:
		cal1, cal2 = _cal1, _cal2
	else:
		cal1, cal2 = calibrateDown()

	print("Setting up oscilloscope to RUN, SEQ, trigger.")
	tds.makeReady()
	print("Start upward scan.")
	tds.trigger()
	zaber.move("ver", command="moveRelative", data=opticDiameter + 20)

	print("creating v1, v2 lists.")
	v1 = tds.getWaveform(ch="CH1")
	v2 = tds.getWaveform(ch="CH2")

	print("Using calibration measurements to... calibrate.")
	dif1 = cal1 - _cal1
	dif2 = cal2 - _cal2
	v1 = list(map(lambda f: f - dif1, v1))
	v2 = list(map(lambda f: f - dif2, v2))

	return x_array, y_array, v1, v2

def move_down():
	"""
	Moves down the diameter of optic and takes measurement every dx
	returns x array, y array, v array
	"""
	global opticDiameter, x_loc, _cal1, _cal2
	x_array = [x_loc]*2500
	y_array = list(np.linspace(0, opticDiameter, 2500))

	if x_loc == 0:
		cal1, cal2, = _cal1, _cal2
	else:
		cal1, cal2 = calibrateHere()

	print("Setting up oscilloscope to RUN, SEQ, trigger.")
	tds.makeReady()

	print("Start downward scan.")
	tds.trigger()
	time.sleep(6.6)
	zaber.move("ver", command="moveRelative", data=-opticDiameter - 20)
	

	print("creating v1, v2 lists.")
	v1 = tds.getWaveform(ch="CH1")
	v2 = tds.getWaveform(ch="CH2")

	print("Using calibration measurements to... calibrate.")
	dif1 = cal1 - _cal1
	dif2 = cal2 - _cal2
	v1 = list(map(lambda f: f - dif1, v1))
	v2 = list(map(lambda f: f - dif2, v2))

	# reverse lists so that they are oriented the same way as when moving up.
	x_array.reverse()
	y_array.reverse()
	v1.reverse()
	v2.reverse()

	return x_array, y_array, v1, v2


def getFileNumber():
	"""
	returns the string of the number file that has yet to be made.
	For example, if the next x array file to made is x_7.txt, this will return
		the string '7.txt'
	"""
	name = "x_1"
	while os.path.isfile("data/" + name + ".txt"):
		new = name.split("_")
		name = new[0] + "_" + str(int(new[1]) + 1)
	number = name.split("_")[1].split(".")[0]
	return number + ".txt"

def calibrateHere():
	"""
	Moves up and takes a calibration measurement.
	returns calibration float
	10 second calibration (not sure how to set the sec/div to anything lower than 1 second)
	"""
	global tds
	tds.setSecDiv("1")

	tds.makeReady()
	tds.trigger()

	print("getting calibration data.")
	cal1 = tds.getAvgOfSamples(ch="CH1", samples=2500)
	cal2 = tds.getAvgOfSamples(ch="CH2", samples=2500)
	tds.setSecDiv("2")
	return cal1, cal2

def calibrateUp():
	"""
	Moves up and takes a calibration measurement.
	returns calibration float
	10 second calibration (not sure how to set the sec/div to anything lower than 1 second)
	"""
	global tds, zaber
	tds.setSecDiv("1")
	zaber.move("ver", command="moveRelative", data = 20)
	time.sleep(5)

	tds.makeReady()
	tds.trigger()

	print("getting calibration data.")
	cal1 = tds.getAvgOfSamples(ch="CH1", samples=2500)
	cal2 = tds.getAvgOfSamples(ch="CH2", samples=2500)
	zaber.move("ver", command="moveRelative", data = -20)
	time.sleep(5)
	tds.setSecDiv("2")
	return cal1, cal2

def calibrateDown():
	"""
	Moves down and takes a calibration measurement.
	returns calibration float
	10 second calibration (not sure how to set the sec/div to anything lower than 1 second)
	"""
	global tds, zaber
	tds.setSecDiv("1")
	zaber.move("ver", command="moveRelative", data = -20)
	time.sleep(5)

	tds.makeReady()
	tds.trigger()

	print("getting calibration data.")
	cal1 = tds.getAvgOfSamples(ch="CH1", samples=2500)
	cal2 = tds.getAvgOfSamples(ch="CH2", samples=2500)
	zaber.move("ver", command="moveRelative", data = 20)
	time.sleep(7)
	tds.setSecDiv("2")
	return cal1, cal2

start_time = time.time()
if __name__ == "__main__":
	traversed = 0
	pass_number = 1
	num = getFileNumber()
	global _cal1, _cal2

	_cal1, _cal2 = calibrateDown()

	while traversed <= opticDiameter:
		print("")
		print("Beginning snake function")
		print("pass number " + str(pass_number) + " of " + str(numScans))
		print(str(time.time() - start_time) + " seconds elapsed so far.")
		pass_number += 2
		temp_x, temp_y, temp_v1, temp_v2 = snake(dx, zaber, tds)
		traversed += 2 * dx
		print("snake finished.")
		print("Appending master lists")
		x.append(temp_x[0])
		x.append(temp_x[1])
		y.append(temp_y[0])
		y.append(temp_y[1])
		v1.append(temp_v1[0])
		v1.append(temp_v1[1])
		v2.append(temp_v2[0])
		v2.append(temp_v2[1])

		time_elapsed = time.time() - start_time
		# write data into text files, just in case something screws up
		#     we will still have all the data we took before the crash.
		with open("data/x_" + num, "a") as f:
			f.write(" ".join(list(map(str, temp_x[0]))) + "\n" + " ".join(list(map(str, temp_x[1]))) + "\n")
		with open("data/y_" + num, "a") as f:
			f.write(" ".join(list(map(str, temp_y[0]))) + "\n" + " ".join(list(map(str, temp_y[1]))) + "\n")
		with open("data/v1_" + num, "a") as f:
			f.write(" ".join(list(map(str, temp_v1[0]))) + "\n" + " ".join(list(map(str, temp_v1[1]))) + "\n")
		with open("data/v2_" + num, "a") as f:
			f.write(" ".join(list(map(str, temp_v2[0]))) + "\n" + " ".join(list(map(str, temp_v2[1]))) + "\n")

		# also write a file which tells the elapsed time
		with open("data/time_" + num, "w") as f:
			f.write("Calibrated: " + str(pass_number) + "/" + str(numScans) + " in " + str(time_elapsed) + " seconds.")

	# print(x)
	# print(y)
	# print(v1)
	# print(v2)

	# Not doing this bit.  Storing positions seems finicky.  did not work as expected.
	# return to starting position
	# dev.zaberMoveToStoredLocation(dev.translation["hor"], 14)
	# dev.zaberMoveToStoredLocation(dev.translation["ver"], 15)
	# print dev.zaberMove("hor", command = dev.cmd["moveRelative"], data=(-opticDiameter))
	
	# got rid of end plotting script.
	#     Just use the conFromFiles.py file.