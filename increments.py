import pendulum, json

# def writenew(flow, power, local_date):
# 	with open(filename, 'w+') as wfile:
# 		wfile.write("slots\tcurrent\tkWh\n")
# 		for i in range(index2-index1):
# 			wfile.write(str(flow[index1+i])
# 			wfile.write()
def main():

	with open("alldata.txt", "r") as f:
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
		# indexes=[0]
		# temp = local_date[0]
		# for i in range(len(local_date)-1):
		# 	if temp != local_date[i+1]:
		# 		temp = local_date[i+1]
		# 		indexes.append(i+1)
		

	# # 	for i in range(unique):
	# 		Fout = deviceID[0] + "-" + local_date[0] + ".txt"
	# 		with open(Fout, 'w+') as wfile:	
	# 			wfile.write("slots\tcurrent\tkWh\n")
	
	# for i in range(int(len(json_data["statuses"])/96)):
	# 	Fout = json_data["statuses"][i]["device"] + "-" + json_data["statuses"][i*97]["date"].replace(".000Z", "").split("T")[0] + ".txt"
	# 	with open(Fout, 'w+') as wfile:
	# 		with open("newcase.txt", 'w+') as newcase:
	# 			wfile.write("utcTime\tslots\tcurrent\tkWh\n")
	# 			hour = 0
	# 			minute = 0
	# 			temp = json_data["statuses"][i]["date"]
	# 			x=0 
	# 			while temp == json_data["statuses"][x+i*96]["date"]:
	# 				if json_data["statuses"][x+i*96]["type"] == "relay":
	# 					newcase.write(str(i) + '\n')
	# 				elif json_data["statuses"][x+i*96]["type"] == "update":
	# 					current = json_data["statuses"][x+i*96]["info"]["current"]
	# 					power = json_data["statuses"][x+i*96]["info"]["power"]
	# 					utcTime = json_data["statuses"][x+i*96]["date"]
	# 					wfile.write(utcTime + '\t')
	# 					wfile.write(str(hour).zfill(2) + ":" + str(minute).zfill(2) + '\t')
	# 					wfile.write(str(current) + '\t')
	# 					wfile.write(str(power) + '\n')
	# 					minute +=15
	# 					if minute >=60:
	# 						minute = 0
	# 						hour += 1
	# 						if hour >23:
	# 							hour = 0
	# 					temp = json_data["statuses"][x+i*96]["date"]
	# 				x+=1

if __name__ == "__main__":
	main()