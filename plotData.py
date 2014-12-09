"""
plotData.py
reads x, y, v1, and v2 array files and creates plots from them
"""
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


num = input("What file number would you like to plot?  (integer): ")
num = "_" + str(num) + ".txt"
print("Attempting to read data/x" + num)
print("Attempting to read data/y" + num)
print("Attempting to read data/v1" + num)
print("Attempting to read data/v2" + num)

length_test = 0
x = []
y = []
v1 = []
v2 = []

with open("data/v1" + num, "r") as f:
	for line in f:
		length_test += 1

make_square = 1800//length_test

# with open("data/x" + num, "r") as f:
# 	for line in f:
# 		line = list(map(float, line.rstrip().split()))
# 		for i in range(make_square):
# 			x.append(line)

# with open("data/y" + num, "r") as f:
# 	for line in f:
# 		line = list(map(float, line.rstrip().split()))
# 		for i in range(make_square):
# 			y.append(line)

with open("data/v1" + num, "r") as f:
	for line in f:
		line = list(map(float, line.rstrip().split()))
		for i in range(make_square):
			v1.append(line[:1801])

with open("data/v2" + num, "r") as f:
	for line in f:
		line = list(map(float, line.rstrip().split()))
		for i in range(make_square):
			v2.append(line[:1801])

# x = np.array(x)
# debug by seeing what x_array looks like.  Was appending strings on accident.  Changed to float.
# print(x)
# y = np.array(y)
v1 = np.array(v1)
v2 = np.array(v2)
# vtot = v2 - v1

# Should already be in meshgrid format?
# plt.contourf(x, y, v2)
plt.figure()
plt.imshow(v1, cmap=cm.Greys_r)

# plt.figure()
# plt.imshow(v2)

plt.figure()
plt.imshow(v1 + v2, cmap=cm.Greys_r)

plt.show()