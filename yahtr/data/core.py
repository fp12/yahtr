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


def local_save_single(folder, file_id, ext, data):
    with open(folder + file_id + ext, 'w') as f:
        if ext == '.json':
            json.dump(data, f, indent=4)


class DataTemplate:
    """
    Abstract base class (most likely a contract)
    for data template classes
    """

    __path: str = 'data/'  #: path to assets
    __ext: str = '.json'  #: extension
    __attributes = []  #: attributes to get

    local_load = local_load
    local_load_single = local_load_single
    local_save_single = local_save_single

    def __init__(self, file_id, **kwargs):
        self.file_id = file_id
        parent = kwargs.get('parent')
        self.parents = [parent] if parent else []

    def add_dependency(self, obj):
        self.parents.append(obj)

    def __dir__(self):
        return super().__dir__() + self.__attributes
