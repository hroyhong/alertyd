import http.client
import json
import os
def generate_text(prompt):

    conn = http.client.HTTPSConnection("api.chesspnt.com")
    payload = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
    })
    headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.getenv("CHESSPNT_API_KEY"),
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json'
    }
   
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")