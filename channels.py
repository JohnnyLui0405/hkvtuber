import requests
import bs4
import json

r = requests.get('https://vtuber.hk/channels.html')
r.encoding = "utf-8"
soup = bs4.BeautifulSoup(r.text,'html.parser')
data = []
useful = False
for link in soup.find_all('a'):
    try:
        channelurl = link.get('href')
        channelname = link.find("div", class_="detail").find("div", class_="title")
        data.append({"url":channelurl, "name":channelname.string})
    except:
        pass
with open("./channels.json" ,mode="w") as jfile:
    json.dump(data,jfile)


