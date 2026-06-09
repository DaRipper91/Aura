import requests
print(requests.post('http://127.0.0.1:11435/api/chat', json={
    "model": "phi3:mini",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": False
}).status_code)
