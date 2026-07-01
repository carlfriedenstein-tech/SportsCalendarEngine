import json
import requests

url = "https://api.pulselive.motogp.com/motogp/v1/events/259be6f4-c23c-4dc2-bc42-7664842f6409"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
)

response.raise_for_status()

data = response.json()

print(json.dumps(data, indent=2))