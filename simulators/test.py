import json

f = open('../data/roomCode.json', "w")
JSON_DATA = {
    "roomCode": "hello"
}
print(JSON_DATA)
json.dump(JSON_DATA, f)
f.close()