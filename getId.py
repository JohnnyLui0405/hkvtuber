import json

with open('./json/channels.json') as jfile:
    datas = json.load(jfile)

for data in datas:
    ID = data["url"].split("/channel/")[1]
    data.update({"channelId":ID})
print(datas)

with open('./json/channels.json', mode="w") as jfile:
    json.dump(datas,jfile)