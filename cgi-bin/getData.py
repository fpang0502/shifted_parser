# import json, requests
#
# headers = {
#     'Authorization': 'Bearer: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InJKZVBud3JRUSIsImV4cCI6MTU2Mjk3NjIxNiwiaWF0IjoxNTMxNDQwMjE2fQ.hmngHavclf9WTvrzn846yP3xRGbYSDEIRovcFw9KlrY',
#     'Content-Type': 'application/json',
# }
# url = "https://api.automategreen.com/v1/statuses?device=" + "HyErn3Blm"
# date = "&date[start]=" + "2018-08-01" + "&date[end]=" + "2018-08-02"
# response = requests.get(url+date, headers=headers)
# json_data = json.loads(response.text)
# with open("api_data.json", "w") as f:
#     json.dump(json_data, f, indent=4, sort_keys=True)

import datetime, pytz

dt_utcnow = datetime.datetime.now(tz=pytz.UTC)
print("This is the current UTC:", dt_utcnow)
dt_mtn = datetime.datetime.now()

mtn_tz = pytz.timezone('US/Mountain')

dt_mtn = mtn_tz.localize(dt_mtn)
print("This is localized Mtn time: ", dt_mtn)
dt_east = dt_mtn.astimezone(pytz.timezone('US/Eastern'))
print("This is eastern time: ", dt_east)
