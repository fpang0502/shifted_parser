import json, requests
'''
This file is only for grabbing data from the specifed dates below
'''
headers = {
    'Authorization': 'Bearer: REDACTED',
    'Content-Type': 'application/json',
}
url = "https://api.automategreen.com/v1/statuses?device=" + "REDACTED"
date = "&date[start]=" + "2018-07-09" + "&date[end]=" + "2018-07-10"
response = requests.get(url+date, headers=headers)
json_data = json.loads(response.text)
with open("api_data.json", "w") as f:
    json.dump(json_data, f, indent=4, sort_keys=True)
