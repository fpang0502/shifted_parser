import json, requests, pytz, datetime
from increments import getIncrements

def main():
	with open("input-master.db", "r+") as input:
		title = input.readline()
		entireFile = input.read()
		inputList=entireFile.split('\n')
		for line in inputList:
			if line.strip():
				info = line.split()
				device = info[0]
				specifiedTimezone = info[1]
				startDate = info[2]
				lastUpdated = info[3]
				fmt = '%Y-%m-%d %H:%M:%S'
				fmtDate = '%Y-%m-%d'
				temp_dt = datetime.datetime.utcnow().strftime(fmt)
				date_time = temp_dt.split()
				date = date_time[0].split('-')
				time = date_time[1].split(':')
				utcToday_dt = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(time[0]),int(time[1]),int(time[2]), tzinfo=pytz.utc)
				locToday_dt = utcToday_dt.astimezone(pytz.timezone(specifiedTimezone))
				locToday = locToday_dt.strftime(fmtDate)
				twoDaysAhead_dt = (locToday_dt + datetime.timedelta(days=2))
				twoDaysAhead = twoDaysAhead_dt.strftime(fmtDate)
				collectData(device, specifiedTimezone, lastUpdated, twoDaysAhead)
				getIncrements(device, specifiedTimezone)
				updateInputMaster(device, locToday)


def update_data(device, startDate, endDate):
	# Update the json_data with the respective date given
	headers = {
	    'Authorization': 'Bearer: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InJKZVBud3JRUSIsImV4cCI6MTU2Mjk3NjIxNiwiaWF0IjoxNTMxNDQwMjE2fQ.hmngHavclf9WTvrzn846yP3xRGbYSDEIRovcFw9KlrY',
	    'Content-Type': 'application/json',
	}
	url = "https://api.automategreen.com/v1/statuses?device=" + device
	date = "&date[start]=" + startDate + "&date[end]=" + endDate
	response = requests.get(url+date, headers=headers)
	json_data = json.loads(response.text)
	with open("api_data.json", "w") as f:
		json.dump(json_data, f, indent=4, sort_keys=True)

def collectData(device, timezone, startDate, endDate):
	update_data(device, startDate, endDate)

	with open("api_data.json", "r") as data:
		json_data = json.load(data)
		updateString = "./" + device + "/" + device + "updates.db"
		updateFile = open(updateString, "a")
		relayString = "./" + device + "/" + device + "relays.db"
		relayFile = open(relayString, "a")
		updateArray=[]
		relayArray=[]
		triggerArray=[]
		for i in range(len(json_data["statuses"])):
			if json_data["statuses"][i]["type"] == "update":
				# Append all the updates
				tempUpdate = json_data["statuses"][i]
				updateArray.append(tempUpdate)

			elif json_data["statuses"][i]["type"] == "relay":
				# Append all the relays
				tempRelay = json_data["statuses"][i]
				relayArray.append(tempRelay)

			elif json_data["statuses"][i]["type"] == "trigger":
				# Append all the triggers
				tempTrigger = json_data["statuses"][i]
				triggerArray.append(tempTrigger)
		writeUpdates(device, updateString, updateFile, updateArray, timezone)
		writeRelays(device, relayString, relayFile, relayArray, triggerArray, timezone)

def writeUpdates(device, updateString, updateFile, updateArray, timezone):
	# Write the update array to deal with duplicates

	for i in range(len(updateArray)):
		utc = updateArray[i]["date"]
		local_date = getLocalDateTime(utc, timezone, "date")
		#print(utc)
		#print(local_date)
		local_time = getLocalDateTime(utc, timezone, "time")
		#print(local_time + '\n')
		current = updateArray[i]["info"]["current"]
		flow = updateArray[i]["info"]["flow"]
		if flow == None:
			flow = "null"
			power = updateArray[i]["info"]["power"]
		textToSend = device +'\t'+ flow +'\t'+ str(current) +'\t'+ str(power) +'\t' + local_date +'\t'+ local_time +'\t'+ utc +'\n'

		if isUnique(updateString, 192, textToSend):
			updateFile.write(textToSend)

def writeRelays(device, relayString, outfile, relayArray, triggerArray, timezone):
	# Write the relay array to deal with Emergency Events and FFR Events
	ffrEvent = False
	emergencyEvent = False
	eventOn = False
	reasonOff = ''
	reasonOn = ''
	utcOff = ''
	utcOn = ''
	dateOff = ''
	dateOn = ''
	timeOff = ''
	timeOn = ''
	tripFreq = ''
	tripTime = ''
	returnFreq = ''
	returnTime = ''
	for i in range(len(relayArray)):
		relayOn = relayArray[i]["info"]["on"]
		if relayOn==False and eventOn==False:
			# If the relay turned off and there was no reported event
			eventOn = True
			reasonOff = relayArray[i]["reason"]
			utcOff = relayArray[i]["date"]
			dateOff = getLocalDateTime(utcOff, timezone, 'date')
			timeOff = getLocalDateTime(utcOff, timezone, 'time')
			if reasonOff == "api":
				# The reason turned off was API
				ffrEvent = False
				emergencyEvent = True
			elif reasonOff == "ffr":
				# The reason turned off was FFR
				emergencyEvent = False
				ffrEvent = True
				tripFreq = str(matchToTrigger(utcOff, triggerArray))
				tripTime = timeOff
		elif relayOn==False and eventOn==True and ffrEvent==True:
			# If the relay is off while there is an FFR Event
			utcReturn = relayArray[i]["date"]
			returnTime = getLocalDateTime(utcReturn, timezone, 'time')
			returnFreq = str(matchToTrigger(utcReturn, triggerArray))

		elif relayOn==True and eventOn==True:
			# If the relay is back on after an event
			eventOn = False
			reasonOn = relayArray[i]["reason"]
			utcOn = relayArray[i]["date"]
			dateOn = getLocalDateTime(utcOn, timezone, 'date')
			timeOn = getLocalDateTime(utcOn, timezone, 'time')
			if reasonOn == "api" and emergencyEvent == True:
				emergencyEvent = False
				textToSend = device +'\t'+ reasonOff +'\t'+ reasonOn +'\t'+ utcOn +'\t'+ dateOff +'\t'+ dateOn +'\t'+ timeOff +'\t'+ timeOn +'\n'
				if isUnique(relayString, 20, textToSend):
					outfile.write(textToSend)
			elif reasonOn == "auto" and emergencyEvent == True:
				emergencyEvent = False
				textToSend = device +'\t'+ reasonOff +'\t'+ reasonOn +'\t'+ utcOn +'\t'+ dateOff +'\t'+ dateOn +'\t'+ timeOff +'\t'+ timeOn +'\n'
				if isUnique(relayString, 20, textToSend):
					outfile.write(textToSend)
			elif reasonOn == "auto" and ffrEvent == True:
				ffrEvent = False
				text = device +'\t'+ reasonOff +'\t'+ reasonOn +'\t'+ utcOn +'\t'+ dateOff +'\t'+ dateOn +'\t'+ timeOff +'\t'+ timeOn +'\t'
				extra = tripFreq +'\t'+ tripTime +'\t'+ returnFreq +'\t'+ returnTime +'\n'
				textToSend = text + extra
				if isUnique(relayString, 20, textToSend):
					outfile.write(textToSend)

def readLastLines(file, lines):
	with open(file, "r") as f:
		f.readline()
		contents = f.readlines()[-lines:]
		return contents

def isUnique(filename, lines, textToSend):
	linesOfFile = readLastLines(filename, lines)
	found = False
	for i in range(len(linesOfFile)):
		if textToSend == linesOfFile[i]:
			found = True
	if found == False:
		return True
	elif found == True:
		return False

def matchToTrigger(utcTime, triggerArray):
	# Match the given UTC time to the time in the trigger array
	for i in range(len(triggerArray)):
		if triggerArray[i]["date"] == utcTime:
			return triggerArray[i]["info"]["frequency"]

def getLocalDateTime(utc, timezone, option):
	# Return the local date or time given UTC
	fmt = '%Y-%m-%d %H:%M:%S'
	fmtDate = '%Y-%m-%d'
	fmtTime = '%H:%M:%S'
	utc = utc.replace(".000Z", "")
	date_time = utc.split("T")
	#print(date_time)
	date = date_time[0].split("-")
	time = date_time[1].split(":")
	utc_dt = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]), tzinfo=pytz.utc)
	local_dt = utc_dt.astimezone(pytz.timezone(timezone))
	local_date = local_dt.strftime(fmtDate)
	local_time = local_dt.strftime(fmtTime)
	#print(local_date)
	#print(local_time)
	#print(local_date, local_time, '\n')
	if option == "date":
		return local_date
	elif option =="time":
		return local_time

def updateInputMaster(device, lastUpdated):
	entireText =''
	with open("input-master.db", "r") as f:
		title = f.readline()
		entireText += title
		devices = f.readlines()
		for i in range(len(devices)):
			if device in devices[i]:
				temp = devices[i].strip('\n')
				indexes = temp.split()
				temp = temp.replace(indexes[3], lastUpdated)
				entireText += temp
			else:
				entireText += devices[i]
	with open("input-master.db", "w+") as f:
		f.write(entireText)

if __name__ == "__main__":
	main()
