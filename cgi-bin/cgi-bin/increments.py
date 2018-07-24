#!/usr/bin/python

import pendulum, json

def main():
	with open("updates.txt", "r") as f:
		labels = f.readline()
		lines = f.read()
		lines = lines.split('\n')
		deviceID = []
		current =[]
		power = []
		local_date = []
		local_time = []
		utcTime = []

		for line in lines:
			temp = line.split()
			if temp != []:
				deviceID.append(temp[0])
				current.append(temp[2])
				power.append(temp[3])
				local_date.append(temp[4])
				local_time.append(temp[5])
				utcTime.append(temp[6])

		for i in range(int(len(local_date)/96)):
			Fout = deviceID[i*96] + "-" + local_date[i*96] + ".txt"
			with open(Fout, 'w+') as wfile:
				wfile.write("slots\tcurrent\tkWh\n")
				hour=0
				minutes=0
				for x in range(96):
					wfile.write(str(hour).zfill(2) + ":" + str(minutes).zfill(2) + '\t')
					wfile.write(str(current[x+i*96]) + '\t')
					wfile.write(str(power[x+i*96]) + '\n')
					minutes +=15
					if minutes >=60:
						minutes = 0
						hour += 1
						if hour >23:
							hour = 0

if __name__ == "__main__":
	main()
