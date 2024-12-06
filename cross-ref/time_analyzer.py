import matplotlib.pyplot as plt
import json

base_timed_fetch_keys = {"resolvedDoi" : [], "firstAuthorInfo": [], "firstAuthorAffiliationInfo": []}

with open("stats.json", "r") as file:
    content = json.loads(file.read())
    
    for item in content:
        for key in base_timed_fetch_keys:
            if (item[key]):
                base_timed_fetch_keys[key].append(item[key]["time"] / 10**9) # time in nanos
           
x = range(len(base_timed_fetch_keys["resolvedDoi"]))     
y1 = base_timed_fetch_keys["resolvedDoi"]
y2 = base_timed_fetch_keys["firstAuthorInfo"]
y3 = base_timed_fetch_keys["firstAuthorAffiliationInfo"]
plt.xticks(x)
plt.plot(x, y1, color='blue', label="DOI reolution")
plt.plot(x, y2, color='green', label="Author Metadata")
plt.plot(x, y3, color='red', label="Affilition Metadata")
plt.legend()
plt.xlabel("2-second spaced API calls")
plt.ylabel("Time taken by API call in seconds")
plt.savefig("time_plot.png")