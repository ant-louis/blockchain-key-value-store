import json
import time
from requests import get


get("http://127.0.0.1:5000/bootstrap", params={"bootstrap":"127.0.0.1:5000"})
get("http://127.0.0.1:5003/bootstrap", params={"bootstrap":"127.0.0.1:5000"})

i = 0
while True :
    i += 11
    get("http://127.0.0.1:5003/put", data=json.dumps({"key":"Team", "value": i, "origin": "127.0.0.1:5005"}))
    time.sleep(2)