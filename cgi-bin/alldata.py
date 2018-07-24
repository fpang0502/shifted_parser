import json, pendulum, requests
from increments import getIncrements

def main():
	with open("input-master.db", "r") as input:
		input.readline()
		inputList = input.read().split('\n')
		for line in inputList:
			if line.strip():
				info = line.split()
				device = info[0]
				timezone = info[1]
				startDate = info[2]
				today = pendulum.today()
				todaysDate = today.to_date_string()
				collectData(device, timezone, startDate, todaysDate)
				getIncrements(device)

def collectData(device, timezone, startDate, todaysDate):
	update_data(device, startDate, todaysDate)
	with open("api_data.json", "r") as data:
		json_data = json.load(data)
		update = open("./" + device + "/" + device + "updates.db", "w+")
		relays = open("./" + device + "/" + device + "relays.db", "w+")
		update.write("deviceID\tflowData\tcurrent\twatthourData\tlocalDate\tlocalTime\tUTCtime\n")
		relays.write("deviceID\treasonOff\treasonOn\tUTC\tdateOff\tdateOn\ttimeOff\ttimeOn\ttripFreq\ttripTime\treturnFreq\treturnTime\n")
		relayArray=[]
		triggerArray=[]
		for i in range(len(json_data["statuses"])):
			utc = json_data["statuses"][i]["date"]
			local_date = getLocalDateTime(utc, timezone, "date")
			local_time = getLocalDateTime(utc, timezone, "time")

			if json_data["statuses"][i]["type"] == "update":
				# Write to the master file
				current = json_data["statuses"][i]["info"]["current"]
				flow = json_data["statuses"][i]["info"]["flow"]
				if flow == None:
					flow = "null"
				power = json_data["statuses"][i]["info"]["power"]
				writeUpdate(update, device, flow, current, power, local_date, local_time, utc)

			elif json_data["statuses"][i]["type"] == "relay":
				# Append all the relays
				tempRelay = json_data["statuses"][i]
				relayArray.append(tempRelay)

			elif json_data["statuses"][i]["type"] == "trigger":
				# Append all the triggers
				tempTrigger = json_data["statuses"][i]
				triggerArray.append(tempTrigger)
		writeRelays(device, relays, relayArray, triggerArray, timezone)

def update_data(device, startDate, todaysDate):
	# Update the json_data with the respective date given
	headers = {
	    'Authorization': 'Bearer: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InJKZVBud3JRUSIsImV4cCI6MTU2Mjk3NjIxNiwiaWF0IjoxNTMxNDQwMjE2fQ.hmngHavclf9WTvrzn846yP3xRGbYSDEIRovcFw9KlrY',
	    'Content-Type': 'application/json',
	}
	url = "https://api.automategreen.com/v1/statuses?device=" + device
	date = "&date[start]=" + startDate + "&date[end]=" + todaysDate
	response = requests.get(url+date, headers=headers)
	json_data = json.loads(response.text)
	with open("api_data.json", "w") as f:
		json.dump(json_data, f, indent=4, sort_keys=True)

def writeRelays(device, outfile, relayArray, triggerArray, timezone):
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
				outfile.write(device +'\t'+ reasonOff +'\t'+ reasonOn +'\t'+ utcOn +'\t'+ dateOff +'\t'+ dateOn +'\t'+ timeOff +'\t'+ timeOn +'\n')
			elif reasonOn == "auto" and emergencyEvent == True:
				emergencyEvent = False
				outfile.write(device +'\t'+ reasonOff +'\t'+ reasonOn +'\t'+ utcOn +'\t'+ dateOff +'\t'+ dateOn +'\t'+ timeOff +'\t'+ timeOn +'\n')
			elif reasonOn == "auto" and ffrEvent == True:
				ffrEvent = False
				outfile.write(device +'\t'+ reasonOff +'\t'+ reasonOn +'\t'+ utcOn +'\t'+ dateOff +'\t'+ dateOn +'\t'+ timeOff +'\t'+ timeOn +'\t')
				outfile.write(tripFreq +'\t'+ tripTime +'\t'+ returnFreq +'\t'+ returnTime +'\n')

def matchToTrigger(utcTime, triggerArray):
	# Match the given UTC time to the time in the trigger array
	for i in range(len(triggerArray)):
		if triggerArray[i]["date"] == utcTime:
			return triggerArray[i]["info"]["frequency"]

def getLocalDateTime(utc, timezone, option):
	# Return the local date or time given UTC
	utc = utc.replace(".000Z", "")
	date_time = utc.split("T")
	date = date_time[0].split("-")
	time = date_time[1].split(":")
	pendulum_datetime = pendulum.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]), tz = timezone)
	local_date = pendulum_datetime.to_date_string()
	pendulum_time = pendulum_datetime.to_time_string()
	string = str(pendulum_datetime)
	addsub = int(string[20:22])
	temp = str(pendulum_time)
	hour = int(temp[0:2])
	if "+" in str(pendulum_datetime):
		hour += addsub
	else:
		hour -= addsub
	if hour>23:
		hour -=24
	elif hour<0:
		hour +=24
	local_time = str(hour).zfill(2)+str(pendulum_time[2:])
	if option == "date":
		return local_date
	elif option =="time":
		return local_time

def writeUpdate(outfile, device, flow, current, power, local_date, local_time, utc):
	# Write the updates to the file given
	outfile.write(device + '\t')
	outfile.write(flow + '\t')
	outfile.write(str(current) + '\t')
	outfile.write(str(power) + '\t')
	outfile.write(local_date + '\t')
	outfile.write(local_time + '\t')
	outfile.write(utc + '\n')

if __name__ == "__main__":
	main()
