import copy


def copy_from_instance(a, b, *args):
    for arg in args:
        attr = getattr(a, arg, None)
        if isinstance(attr, list):
            setattr(b, arg, attr[:])
        else:
            setattr(b, arg, copy.copy(attr))


def get_from_dict(a, data, *args):
    for arg in args:
        setattr(a, arg, data[arg] if arg in data else None)
