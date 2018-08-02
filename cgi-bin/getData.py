import json, requests

headers = {
    'Authorization': 'Bearer: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6InJKZVBud3JRUSIsImV4cCI6MTU2Mjk3NjIxNiwiaWF0IjoxNTMxNDQwMjE2fQ.hmngHavclf9WTvrzn846yP3xRGbYSDEIRovcFw9KlrY',
    'Content-Type': 'application/json',
}
url = "https://api.automategreen.com/v1/statuses?device=" + "HyErn3Blm"
date = "&date[start]=" + "2018-07-25" + "&date[end]=" + "2018-07-26"
response = requests.get(url+date, headers=headers)
json_data = json.loads(response.text)
with open("api_data.json", "w") as f:
    json.dump(json_data, f, indent=4, sort_keys=True)

with open("api_data.json", "r") as f:
    json_data = json.load(f)
    count=0
    for i in range(len(json_data["statuses"])):
        if json_data["statuses"][i]["type"] == "update":
            count+=1
            print(count, json_data["statuses"][i]["date"])
        if count%4 == 0:
            print('\n')
