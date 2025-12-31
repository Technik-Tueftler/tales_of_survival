import requests

url = "http://192.168.178.4:5002"

payload = {"text": "Hallo Welt"}

print("Requesting TTS")
request = requests.get(url, params=payload, timeout=90)

print("Return stuff")

with open("output.wav", "wb") as f:
    for chunk in request.iter_content(chunk_size=128):
        f.write(chunk)
print("finished")
