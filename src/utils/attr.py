import copy


def copy_from_instance(a, b, *args):
    for arg in args:
        attr = getattr(a, arg)
        if isinstance(attr, list):
            setattr(b, arg, attr[:])
        else:
            setattr(b, arg, copy.copy(attr))


def get_from_dict(a, data, *args):
    for arg in args:
        if arg in data:
            setattr(a, arg, data[arg])
