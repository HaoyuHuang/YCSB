#!/usr/bin/python
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import sys
filenames = []
filenames.append(sys.argv[2]+'cpu.txt')
filenames.append(sys.argv[2]+'mem.txt')
filenames.append(sys.argv[2]+'disk.txt')
filenames.append(sys.argv[2]+'net.txt')
filenames.append(sys.argv[2]+'diskRW.txt')

path = str(sys.argv[1]) #'C:\\Users\\yaz\\Documents\\BG\\BGServerListenerLogs\\Exp1426007481104-nummembers100000-numclients3-bmoderetain-threadcount100-logfalse\\'
#print(sys.argv[1])

for file in filenames:
	with open(path+file) as f:
		data = f.read()
		
	data = data.splitlines()
	#print(data)
	
	# get the name
#	name = data[0].split(',')[0]
        #name = 'CPU'
                  
	# get offlines value
	#offlines = data[len(data)-2]

	# remove some unsed data
	#data = data[3:len(data)-2]

	# get probabilities data
	colnum = len(data[0].split(',')) - 1
	#print(colnum)
	if colnum ==0:
		colnum=1

	headers = data[0].split(',')
	start = 1
	try:
		float(headers[0])
		start = 0
		for x in range(0, colnum):
			headers[x] = str(x)
	except ValueError:
		start = 1		

	cols = []
	for c in range(0, colnum):
		cols.append([row.split(',')[c] for row in data[start:]])
	
	#for c in range(0, colnum):
	#	print(cols[c])

	# process drawing plots
	#cols = [2, 4, 6, 8, 10]

	figMR = plt.figure()
	axMR = figMR.add_subplot(111)
	axMR.set_title(file)
	axMR.set_xlabel('Time')
	if 'cpu' in file:
		axMR.set_ylabel('%Utilization')	
#		plt.ylim( 0, 100 )
	if 'mem' in file:
		axMR.set_ylabel('available MB')
#		plt.ylim( 0, 16300 )
	if 'net' in file:
		axMR.set_ylabel('MB/sec')
#		plt.ylim( 0, 120 )		
	if 'disk' in file:
		axMR.set_ylabel('Queue length')		
	if 'diskRW' in file:
		axMR.set_ylabel('Number of sectors/sec')
	
	xAxis = []
	for i in range(0, len(cols[0])):
		xAxis.append(i)	
	i=0
	for col in cols:
		stri = 'client'+str(i)
		axMR.plot(xAxis, col, label= headers[i])
		i=i+1

	if 'disk' in file:
		ymin, ymax = plt.ylim()
		if ymax < 5:
			plt.ylim( 0, 5 )

	art = []
        lgd = axMR.legend(loc=9, bbox_to_anchor=(0.5, -0.1))
        art.append(lgd)
	#leg = axMR.legend()
	#plt.show()
	plt.savefig(path+file+'.png',additional_artists=art, bbox_inches="tight")
	print 'Created ' + path + file + '.png'



