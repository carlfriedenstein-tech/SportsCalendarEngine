import requests
import json

url = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=500&idSeason=285023"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

data = response.json()

print("Top level keys:")
print(data.keys())

print("\nResults contains:", len(data["Results"]), "matches")

print("\nFirst match:\n")
print(json.dumps(data["Results"][0], indent=4))