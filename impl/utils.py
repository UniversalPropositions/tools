import json

def read_config():
  with open("./config/config.json", "r", encoding="utf-8") as f:
    data = f.read()
    config = json.loads(data)
    return config
