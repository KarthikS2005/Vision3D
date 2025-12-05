import requests
import json

url = "http://127.0.0.1:8000/api/generate/"
data = {"prompt": "a blue sphere"}

try:
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print(f"JSON: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
