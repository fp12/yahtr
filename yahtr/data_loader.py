import json
import os


def local_load(folder, ext):
    data = {}
    for dirpath, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(ext):
                with open(dirpath + '/' + file) as f:
                    data_path = dirpath[len(folder):]
                    data_name = data_path + '/' if data_path else ''
                    data_name += file[:-len(ext)]
                    if ext == '.json':
                        data[data_name] = json.load(f)
                    else:
                        data[data_name] = f.readlines()
    return data


def local_load_single(folder, file, ext):
    with open(folder + file + ext) as f:
        if ext == '.json':
            return json.load(f)
        else:
            return f.readlines()
    return {}
