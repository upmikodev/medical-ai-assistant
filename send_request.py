
import requests
import json

url = "http://localhost:8000/interact"
headers = {"Content-Type": "application/json"}
payload = {"message": "Dame la informacion, clasifica y segmentalas imagenes de Marta Kowalska, si la probabilidad de que tenga un tumor es mas del 30%"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise an exception for HTTP errors
    print("Response from backend:", response.json())
except requests.exceptions.RequestException as e:
    print(f"Error sending request: {e}")
