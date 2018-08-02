import json, datetime, pytz

def getIncrements(device, timezone):
	with open("./" + device + "/" + device + "updates.db", "r") as f:
		labels = f.readline()
		lines = f.readlines()
		current =[]
		power = []
		local_date = []
		local_time = []
		#utcTime = []
		appendLists(lines, current, power, local_date, local_time)
		writeIncrements(device, current, power, local_date, local_time, timezone)

def appendLists(lines, current, power, local_date, local_time):
	for line in lines:
		temp = line.split()
		if temp != []:
			#deviceID.append(temp[0])
			current.append(temp[2])
			power.append(temp[3])
			local_date.append(temp[4])
			local_time.append(temp[5])
			#utcTime.append(temp[6])

def lookForDates(local_date):
	uniqueDates = list(set(local_date))
	orderedDates = sortDates(uniqueDates)
	return orderedDates

def sortDates(uniqueDates):
	dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in uniqueDates]
	dates.sort()
	orderedDates = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
	return orderedDates

def writeIncrements(device, current, power, local_date, local_time, timezone):
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
		if orderedDates[x] == locToday or orderedDates[x] == yesterday:
			Fout = "./" + device + "/increments/" + device + "-" + orderedDates[x] + ".db"
			with open(Fout, 'w+') as wfile:
				hour=0
				minutes=0
				listToWrite = []
				for y in range(len(local_date)):
					if orderedDates[x] == local_date[y]:
						stringToWrite = local_date[y] +'\t'+ local_time[y] +'\t'+ str(hour).zfill(2) +":"+ str(minutes).zfill(2) +'\t'+ str(current[y]) +'\t'+ str(power[y]) +'\n'
						listToWrite.append(stringToWrite)
						minutes +=15
						if minutes >=60:
							minutes = 0
							hour += 1
							if hour >23:
								hour = 0
						dateCount+=1
				#if len(listToWrite) < 96:
				wfile.write("localDate\tlocalTime\tslots\tcurrent\tkWh\n")
				for i in range(len(listToWrite)):
					wfile.write(listToWrite[i])
			print(orderedDates[x], dateCount)
			dateCount=0

if __name__ == "__main__":
	main()
