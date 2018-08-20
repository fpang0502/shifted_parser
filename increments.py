
import os, json, datetime, pytz

def getIncrements(device, timezone):
	'''
	This method is to read the master update file and write their respective increment files
	'''
	with open("./devices/" + device + "/" + device + "updates.db", "r") as f:
		labels = f.readline()
		lines = f.readlines()
		current =[]
		power = []
		local_date = []
		local_time = []
		#utcTime = []
		appendLists(lines, current, power, local_date, local_time)
		if not os.path.isdir("./devices/" + device + "/increments"):
			os.makedirs("./devices/" + device + "/increments")
		writeIncrements(device, current, power, local_date, local_time, timezone)

def appendLists(lines, current, power, local_date, local_time):
	'''
	With the lines fed to it, it will extract the current, power, date, and time to lists
	'''
	for line in lines:
		temp = line.split()
		if temp != []:
			#deviceID.append(temp[0])
			current.append(temp[2])
			power.append(temp[3])
			local_date.append(temp[4])
			local_time.append(temp[5])
			#utcTime.append(temp[6])

def lookForDates(local_dates):
	'''
	Removes duplicates of the local dates fed to it using a set and returns a list
	'''
	uniqueDates = list(set(local_dates))
	orderedDates = sortDates(uniqueDates)
	return orderedDates

def sortDates(uniqueDates):
	'''
	Sorts the unique dates into a list of ordered dates
	'''
	dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in uniqueDates]
	dates.sort()
	orderedDates = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
	return orderedDates

def writeIncrements(device, current, power, local_date, local_time, timezone):
	'''
	Formats the dates and writes the increments to their respective files
	'''
	orderedDates = lookForDates(local_date)
	print(orderedDates)
	dateCount=0
	for x in range(len(orderedDates)):
		fmt = '%Y-%m-%d %H:%M:%S'
		fmtDate = '%Y-%m-%d'
		temp_dt = datetime.datetime.utcnow().strftime(fmt)
		date_time = temp_dt.split()
		date = date_time[0].split('-')
		time = date_time[1].split(':')
		utcToday_dt = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(time[0]),int(time[1]),int(time[2]), tzinfo=pytz.utc)
		locToday_dt = utcToday_dt.astimezone(pytz.timezone(timezone))
		yesterday_dt = (locToday_dt + datetime.timedelta(days=-1))
		yesterday = yesterday_dt.strftime(fmtDate)
		locToday = locToday_dt.strftime(fmtDate)
		# if orderedDates[x] == locToday or orderedDates[x] == yesterday:
		Fout = "./devices/" + device + "/increments/" + device + "-" + orderedDates[x] + ".db"
		with open(Fout, 'w+') as wfile:
			wfile.write("localDate\tlocalTime\tslots\tcurrent\tkWh\n")
			hour=0
			minutes=0
			listToWrite = []
			for y in range(len(local_date)):
				if orderedDates[x] == local_date[y]:
					stringToWrite = local_date[y] +'\t'+ local_time[y] +'\t'+ str(hour).zfill(2) +":"+ str(minutes).zfill(2) +'\t'+ str(current[y]) +'\t'+ str(power[y]) +'\n'
					#listToWrite.append(stringToWrite)
					wfile.write(stringToWrite)
					minutes +=15
					if minutes >=60:
						minutes = 0
						hour += 1
						if hour >23:
							hour = 0
					dateCount+=1
			# for i in range(len(listToWrite)):
			# 	wfile.write(listToWrite[i])
		print(orderedDates[x], dateCount)
		dateCount=0

if __name__ == "__main__":
	main()
