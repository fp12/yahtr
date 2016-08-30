import data_loader


class ClassesList:
    def __init__(self):
        self.classes = {}

    def local_load(self, root_path):
        self.classes = data_loader.local_load(root_path + 'data/classes/', '.json')

    def wiki_load(self):
        def parse(raw_file):
            return {'initiative': 12}

        classes = data_loader.wiki_load('Class', parse)

        changed = dict.fromkeys(classes.keys() & self.classes.keys(), {})
        for cls in changed.keys():
            print(cls, classes[cls])
            if classes[cls]:
                for stat_name in classes[cls]:
                    print(stat_name)
                    if stat_name in self.classes[cls]:
                        changed[cls].update({stat_name: {'old': self.classes[cls][stat_name], 'new': classes[cls][stat_name]}})

        removed = [item for item in self.classes.keys() if item not in classes]
        for x in removed:
            del(self.classes[x])

        added = dict([(item, classes[item]) for item in classes.keys() if item not in self.classes])
        self.classes.update(added)

        return added, changed, removed
