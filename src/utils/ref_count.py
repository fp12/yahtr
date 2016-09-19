class RefCounted:
    total_count = 0

    @classmethod
    def get_instances_total_count(cls):
        return cls.total_count

    def __init__(self):
        self.__class__.total_count += 1
