#!/usr/bin/python

import json, pendulum, requests

def main():
	update_data()
	with open("api_data.json", "r") as f:
		json_data = json.load(f)
		device = json_data["statuses"][0]["device"]
		update = open("updates.txt", "w+")
		relay = open(device + "relays.txt", "w+")
		trigger = open("triggers.txt", "w+")
		# test = open("test.txt", "w+")
		update.write("deviceID\tflowData\tcurrent\twatthourData\tlocalDate\tlocalTime\tUTCtime\n")
		relay.write("deviceID\tlocalDate\tlocalStart\tlocalEnd\tUTC\tsetTime\tactualDuration\treason\twatthourDuration\n")
		trigger.write("deviceID\tlocalDate\tlocalTime\tfrequency\tUTC\n")
		relayArray=[]
		for i in range(len(json_data["statuses"])):
			utc = json_data["statuses"][i]["date"]
			local_date = getLocalDateTime(utc, 'US/Hawaii', "date")
			local_time = getLocalDateTime(utc, 'US/Hawaii', "time")

			if json_data["statuses"][i]["type"] == "update":
				current = json_data["statuses"][i]["info"]["current"]
				flow = json_data["statuses"][i]["info"]["flow"]
				if flow == None:
					flow = "null"
				power = json_data["statuses"][i]["info"]["power"]
				writeUpdate(update, device, flow, current, power, local_date, local_time, utc)

			elif json_data["statuses"][i]["type"] == "relay":
				temp = json_data["statuses"][i]
				relayArray.append(temp)

			elif json_data["statuses"][i]["type"] == "trigger":
				frequency = json_data["statuses"][i]["info"]["frequency"]
				writeTrigger(trigger, device, local_date, local_time, str(frequency), utc)

def update_data():
	headers = {
	    'Authorization': 'Bearer: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InJKZVBud3JRUSIsImV4cCI6MTU2Mjk3NjIxNiwiaWF0IjoxNTMxNDQwMjE2fQ.hmngHavclf9WTvrzn846yP3xRGbYSDEIRovcFw9KlrY',
	    'Content-Type': 'application/json',
	}
	url = "https://api.automategreen.com/v1/statuses?device=HyErn3Blm"
	date = "&date[start]=2018-07-12&date[end]=2018-07-19"
	response = requests.get(url+date, headers=headers)
	json_data = json.loads(response.text)
	with open("api_data.json", "w") as f:
		json.dump(json_data, f, indent=4, sort_keys=True)
		# json_data = json.load(f)
		# for i in range(len(data["statuses"])):
		# 	json_data["statuses"].append(data["statuses"][i])
		# with open("api_data.json", "w") as f:
		# 	json.dump(json_data, f, indent=4, sort_keys=True)

def getLocalDateTime(utc, timezone, option):
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

def subtractTimes(start, end):
	ends = end.split(':')
	end_seconds = int(ends[0])*3600 + int(ends[1])*60 + int(ends[2])
	starts = start.split(':')
	start_seconds = int(starts[0])*3600 + int(starts[1])*60 + int(starts[2])
	actualTime = str(end_seconds - start_seconds)
	return actualTime

def writeUpdate(outfile, device, flow, current, power, local_date, local_time, utc):
	outfile.write(device + '\t')
	outfile.write(flow + '\t')
	outfile.write(str(current) + '\t')
	outfile.write(str(power) + '\t')
	outfile.write(local_date + '\t')
	outfile.write(local_time + '\t')
	outfile.write(utc + '\n')

def writeTrigger(outfile, device, local_date, local_time, frequency, utc):
	outfile.write(device + '\t')
	outfile.write(local_date + '\t')
	outfile.write(local_time + '\t')
	outfile.write(str(frequency) + '\t')
	outfile.write(utc + '\n')


	# started=False
	# utc=''
	# start_date=''
	# start_time=''
	# end_time=''
	# setTime=''
	# reason=''
	# for i in range(len(relayArray)):
	# 	# temp = json.dumps(relayArray[i], indent=4, sort_keys=True)
	# 	# test.write(temp)
	# 	print(relayArray[i]["info"])
	# 	if relayArray[i]["info"]["on"] == False and started==False:
	# 		started=True
	# 		utc = relayArray[i]["date"]
	# 		start_date = getLocalDateTime(utc, 'US/Hawaii', "date")
	# 		start_time = getLocalDateTime(utc, 'US/Hawaii', "time")
	# 		setTime = str(relayArray[i]["info"]["toggleIn"])
	# 		reason = relayArray[i]["reason"]
	# 		relay.write(device +'\t')
	# 		relay.write(start_date + '\t')
	# 		relay.write(start_time + '\t')
	# 	if relayArray[i]["info"]["on"] == True and started==True:
	# 		started=False
	# 		end_time = getLocalDateTime(relayArray[i]["date"], 'US/Hawaii', "time")
	# 		actualTime = subtractTimes(start_time, end_time)
	# 		relay.write(end_time + '\t')
	# 		relay.write(utc + '\t')
	# 		relay.write(setTime + '\t')
	# 		relay.write(actualTime + '\t')
	# 		relay.write(reason + '\t')
	# 		relay.write("watthourDuration\n")


if __name__ == "__main__":
	main()
