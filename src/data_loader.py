import json
import os

def simple_load(folder, ext):
    data = {}
    for file in os.listdir(folder):
        if file.endswith(ext):
            with open(folder + file) as f:
                data[file[:-len(ext)]] = json.load(f)
    return data
