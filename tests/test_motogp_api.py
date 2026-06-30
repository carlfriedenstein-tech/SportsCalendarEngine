import requests

url = "https://api.pulselive.motogp.com/motogp/v1/events?seasonYear=2026"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30,
)

response.raise_for_status()

events = response.json()

print(f"Found {len(events)} events\n")

first = events[0]

print("Keys:")
print(first.keys())

print("\nFirst Event:")
print(first)