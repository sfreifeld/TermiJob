import requests
import sqlite3









'''

url = "https://linkedin-jobs-scraper-api.p.rapidapi.com/jobs"

payload = {
	"title": "Software Engineer",
	"location": "Berlin",
	"rows": 100
}
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "23625d3adfmsh11e79f6ffca7060p1f0cabjsn7513e0a2cf0b",
	"X-RapidAPI-Host": "linkedin-jobs-scraper-api.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    try:
        print(response.json())
    except ValueError:
        print("Response is not in JSON format.")
else:
    print(f"Error: {response.status_code}, Content: {response.text}")
'''