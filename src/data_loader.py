import json
import os
import urllib.request
import re


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
        return json.load(f)
    return {}


def wiki_load(data_type, f_parse):
    __BASE_URL = 'https://raw.githubusercontent.com/wiki/fp12/yahtr/'
    __EXT = '.md'
    __RE_FORMAT = r'\[\[(?P<name>[\w ]+)\|(?P<path>\[Design\] {0}: [\w %-]+)\]\]'

    data = {}

    try:
        f = urllib.request.urlopen('{0}Home{1}'.format(__BASE_URL, __EXT))
    except urllib.error.HTTPError as e:
        print(e)
    else:
        raw = f.read().decode("utf-8")
        exp = __RE_FORMAT.format(data_type)
        found = re.findall(exp, raw)
        for x in found:
            url = '{0}{1}{2}'.format(__BASE_URL, x[1].replace(' ', '-'), __EXT)
            try:
                f = urllib.request.urlopen(url)
            except urllib.error.HTTPError as e:
                pass
                # print('Missing data @ ' + url)
            else:
                raw = f.read().decode("utf-8")
                data.update({x[0].lower(): f_parse(raw)})
    return data
