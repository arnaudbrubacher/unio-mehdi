import json

from pprint import pprint
# Opening JSON file
f = open('ElectionGuard API Tests.postman_collection.json')
 
# returns JSON object as
# a dictionary
data = json.load(f)
 
# Iterating through the json
# list
 
# Closing file
f.close()

steps = data["item"][0]["item"]

for step in steps:
    print(step["name"])
    for req in step["item"]:
        print(req["name"])